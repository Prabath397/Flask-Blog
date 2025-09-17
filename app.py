from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
# Secret key for flash messages; keep this secret in production
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET', 'dev-secret-key')

db = SQLAlchemy(app)

# Import models here to register with SQLAlchemy
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Post {self.id} - {self.title}>"

# Create DB if it doesn't exist
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("index.html", posts=posts)

@app.route("/post/<int:post_id>")
def post_detail(post_id):
    p = Post.query.get_or_404(post_id)
    return render_template("post.html", post=p)

@app.route("/create", methods=("GET", "POST"))
def create():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:
            flash("Title and content are required.")
            return redirect(url_for("create"))

        new_post = Post(title=title, content=content)
        db.session.add(new_post)
        db.session.commit()
        flash("Post created successfully.")
        return redirect(url_for("index"))

    return render_template("create_edit.html", action="Create", post=None)

@app.route("/edit/<int:post_id>", methods=("GET", "POST"))
def edit(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:
            flash("Title and content are required.")
            return redirect(url_for("edit", post_id=post_id))

        post.title = title
        post.content = content
        db.session.commit()
        flash("Post updated successfully.")
        return redirect(url_for("post_detail", post_id=post.id))

    return render_template("create_edit.html", action="Edit", post=post)

@app.route("/delete/<int:post_id>", methods=("POST",))
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    # For development only. Use a proper WSGI server in production.
    app.run(debug=True)
