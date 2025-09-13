from django.contrib.auth.hashers import make_password
import logging
from django.core.management.base import BaseCommand

from apps.accounts.models import User
from apps.blog.models import Comment, Like, Post

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, **options) -> None:
        self.stdout.write(self.style.SUCCESS("🔄 Seeding Test Data..."))
        self.generate_data()
        self.stdout.write(self.style.SUCCESS("✅ Test data seeded!"))

    def generate_data(self):
        test_data = self.data_seed()

        # CREATE USERS
        users_to_create = test_data["users"]
        User.objects.bulk_create(
            [
                User(password=make_password(user.pop("password")), **user)
                for user in users_to_create
            ],
            ignore_conflicts=True,
        )

        # CREATE POSTS
        # using the author of the non staff user
        non_staff_user = User.objects.get_or_none(email=users_to_create[1]["email"])
        post_to_create = test_data["post"]
        post, _ = Post.objects.get_or_create(
            author_id=non_staff_user.id, defaults=post_to_create
        )

        # CREATE COMMENTS & REPLIES
        comments_to_create = test_data["comments"]
        staff_user = User.objects.get_or_none(email=users_to_create[0]["email"])
        post = Post.objects.filter(author=non_staff_user).first()
        comment, _ = Comment.objects.get_or_create(
            author=staff_user, post=post, text=comments_to_create[0]
        )
        reply, _ = Comment.objects.get_or_create(
            author=non_staff_user, post=post, parent=comment, text=comments_to_create[1]
        )

        # CREATE LIKES
        Like.objects.bulk_create(
            [
                Like(author=staff_user, post=post),
                Like(author=non_staff_user, comment=comment),
                Like(author=staff_user, comment=reply, is_disliked=True),
            ],
            ignore_conflicts=True,
        )

    def data_seed(self):
        return {
            "users": [
                {
                    "first_name": "Real",
                    "last_name": "Admin",
                    "email": "real.admin@example.com",
                    "password": "password123#",
                    "is_staff": True,
                    "is_superuser": True,
                    "is_email_verified": True,
                },
                {
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                    "password": "password123#",
                    "is_email_verified": True,
                },
            ],
            "post": {
                "title": "First Post",
                "text": "This is the content of the first post.",
            },
            "comments": [
                "This is a comment on the first post.",
                "This is a reply to the comment on the first post.",
            ],
        }
