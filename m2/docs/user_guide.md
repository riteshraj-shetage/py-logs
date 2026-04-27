# SocialApp — User Guide

A complete reference for using the Basic Version of the Social Media Platform.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Registration & Login](#registration--login)
3. [Creating Posts](#creating-posts)
4. [Liking Posts](#liking-posts)
5. [Commenting](#commenting)
6. [Deleting Posts](#deleting-posts)
7. [Admin Interface](#admin-interface)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

```bash
# Navigate to the project directory
cd complete-tasks/m2

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# (Optional) Create an admin superuser
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

Open your browser at **http://127.0.0.1:8000/**

---

## Registration & Login

### Register a new account

1. Click **Register** in the top navigation bar.
2. Fill in: Username, Email, Password, Confirm Password.
3. Click **Create Account**.
4. You are automatically logged in and redirected to the home feed.

### Log in to an existing account

1. Click **Login** in the top navigation bar.
2. Enter your Username and Password.
3. Click **Login**.
4. You are redirected to the home feed.

### Log out

- Click the **Logout** button in the top navigation bar.

---

## Creating Posts

### From the Home Feed (quick post)

1. The home feed shows a **Share something** form at the top.
2. Type your message in the text area.
3. Optionally attach an image (JPG, PNG, GIF, etc.).
4. Click **Post**.
5. Your post appears at the top of the feed immediately.

### From the dedicated Create Post page

1. Click **✏️ New Post** in the navigation bar.
2. Fill in the content field.
3. Optionally attach an image.
4. Click **Publish Post**.

---

## Liking Posts

- On the home feed or post detail page, click the **❤️ Like** button below a post.
- The button turns red and shows the updated count.
- Click **Unlike** to remove your like.
- Likes are unique — you can only like a post once.

---

## Commenting

1. Click the **💬 N Comments** button on any post to open the post detail page.
2. Scroll to the **Add a Comment** form at the bottom.
3. Type your comment and click **Submit Comment**.
4. Your comment appears in the comments list, ordered oldest-first.

---

## Deleting Posts

- Only the author of a post can delete it.
- On the home feed or post detail page, click **🗑 Delete** (visible only on your own posts).
- A browser confirmation dialog will appear — click OK to confirm.

---

## Admin Interface

Django's built-in admin panel is available at **http://127.0.0.1:8000/admin/**

You need a superuser account to access it:

```bash
python manage.py createsuperuser
```

From the admin you can:
- View, edit, and delete any Post, Comment, or Like
- Manage user accounts

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'django'` | Run `pip install -r requirements.txt` |
| `ModuleNotFoundError: No module named 'PIL'` | Run `pip install Pillow` |
| Images not loading | Ensure `MEDIA_ROOT` directory exists; the server serves media files automatically in `DEBUG=True` mode |
| `no such table` error | Run `python manage.py migrate` |
| Can't log in | Check username/password spelling; passwords are case-sensitive |
| Port 8000 already in use | Run `python manage.py runserver 8080` and open `http://127.0.0.1:8080/` |
