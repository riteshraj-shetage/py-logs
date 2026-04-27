# Social Media Platform — Basic Version (m2)

A fully functional Django social media platform implementing the Basic Option:
**Posts**, **Comments**, and **Likes** — with user authentication built in.

---

## Project Structure

```
m2/
├── manage.py
├── requirements.txt
├── db.sqlite3            # created after migrate
├── media/               # uploaded images
├── static/
│   └── css/style.css
├── templates/
│   ├── base.html
│   ├── users/
│   │   ├── login.html
│   │   └── register.html
│   └── posts/
│       ├── home.html
│       ├── create_post.html
│       └── post_detail.html
├── social_platform/     # Django project package
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/               # Auth app
│   ├── forms.py
│   ├── views.py
│   └── urls.py
└── posts/               # Posts, Comments, Likes app
    ├── models.py
    ├── forms.py
    ├── views.py
    ├── urls.py
    └── admin.py
```

---

## Setup & Run

```bash
# 1. Navigate to the project directory
cd complete-tasks/m2

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply database migrations
python manage.py migrate

# 4. (Optional) Create an admin superuser
python manage.py createsuperuser

# 5. Start the development server
python manage.py runserver

# 6. Open in your browser
#    http://127.0.0.1:8000/
```

---

## Features

| Feature | Description |
|---|---|
| **Posts** | Authenticated users can create posts with text and optional image upload |
| **Comments** | Users can comment on any post; comments appear in chronological order |
| **Likes** | Toggle like/unlike on posts; like count shown on home feed and post detail |
| **Authentication** | Register, login, and logout with Django's built-in auth system |
| **Home Feed** | Displays all posts newest-first with inline post creation form |
| **Admin** | Full Django admin at `/admin/` for Post, Comment, Like management |

---

## Tech Stack

- **Backend**: Django 4.2
- **Database**: SQLite (dev) — swap to PostgreSQL for production
- **Frontend**: Bootstrap 5 (CDN) + minimal custom CSS
- **Media**: Pillow for image handling
