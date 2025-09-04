import json, uuid, pytest
from django.test import TestCase
from unittest.mock import patch
from apps.common.exceptions import ErrorCode
from apps.accounts.models import User
from apps.blog.models import Post, Comment, Like
from apps.common.tests import aclient
from apps.accounts.tests import TestAccountsUtil


class TestBlogUtil:
    def sample_post(author: User):
        return Post.objects.create(
            author=author,
            title="Test Blog Post",
            text="This is a test blog post content",
        )

    def sample_comment(author: User, post: Post):
        return Comment.objects.create(
            author=author, post=post, text="This is a test comment"
        )

    def sample_reply(author: User, post: Post, parent_comment: Comment):
        return Comment.objects.create(
            author=author, post=post, parent=parent_comment, text="This is a test reply"
        )


@pytest.mark.django_db
class TestBlogPostsEndpoints(TestCase):
    BASE_URI_PATH = "/api/v1/blog"
    get_posts_url = f"{BASE_URI_PATH}/posts"
    create_post_url = f"{BASE_URI_PATH}/posts"

    def setUp(self):
        self.author = TestAccountsUtil.first_verified_user()
        self.other_user = TestAccountsUtil.second_verified_user()
        self.auth_token = TestAccountsUtil.auth_token(self.author)
        self.other_auth_token = TestAccountsUtil.auth_token(self.other_user)
        self.sample_post = TestBlogUtil.sample_post(self.author)

    # TEST POSSIBLE RESPONSES FOR GET ALL POSTS ENDPOINT
    @patch("apps.blog.schemas.PostFilterSchema.filter")
    async def test_get_posts_successful(self, mock_filter):
        # Mock the filter method to return the queryset unchanged
        mock_filter.side_effect = lambda queryset: queryset

        response = await aclient.get(f"{self.get_posts_url}?page=1&limit=10&search=")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Posts returned successfully")
        self.assertIn("data", response.data)

    @patch("apps.blog.schemas.PostFilterSchema.filter")
    async def test_get_posts_with_pagination(self, mock_filter):
        # Mock the filter method to return the queryset unchanged
        mock_filter.side_effect = lambda queryset: queryset

        response = await aclient.get(f"{self.get_posts_url}?page=1&limit=10&search=")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Posts returned successfully")
        self.assertIn("data", response.data)

    @patch("apps.blog.schemas.PostFilterSchema.filter")
    async def test_get_posts_with_search_filter(self, mock_filter):
        # Mock the filter method to return the queryset unchanged
        mock_filter.side_effect = lambda queryset: queryset

        response = await aclient.get(
            f"{self.get_posts_url}?page=1&limit=10&search=test"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Posts returned successfully")
        self.assertIn("data", response.data)

    # TEST POSSIBLE RESPONSES FOR CREATE POST ENDPOINT
    async def test_create_post_successful(self):
        data = {"title": "New Test Post", "text": "This is a new test post content"}

        response = await aclient.post(
            self.create_post_url,
            data=data,
            headers={"Authorization": f"Bearer {self.auth_token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Post created successfully")
        self.assertIn("data", response.data)

    async def test_create_post_unauthorized(self):
        data = {"title": "New Test Post", "text": "This is a new test post content"}

        response = await aclient.post(self.create_post_url, data=data)
        self.assertEqual(response.status_code, 401)

    # TEST POSSIBLE RESPONSES FOR GET SINGLE POST ENDPOINT
    async def test_get_single_post_successful(self):
        get_post_url = f"{self.BASE_URI_PATH}/posts/{self.sample_post.slug}"

        response = await aclient.get(get_post_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Post returned successfully")
        self.assertIn("data", response.data)

    async def test_get_single_post_not_found(self):
        get_post_url = f"{self.BASE_URI_PATH}/posts/nonexistent-slug"

        response = await aclient.get(get_post_url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["status"], "failure")
        self.assertEqual(response.data["message"], "Post not found")

    # TEST POSSIBLE RESPONSES FOR UPDATE POST ENDPOINT
    async def test_update_post_successful(self):
        update_post_url = f"{self.BASE_URI_PATH}/posts/{self.sample_post.slug}"
        data = {
            "title": "Updated Test Post",
            "text": "This is updated test post content",
        }

        response = await aclient.put(
            update_post_url,
            data=data,
            headers={"Authorization": f"Bearer {self.auth_token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Post updated successfully")
        self.assertIn("data", response.data)

    async def test_update_post_not_found(self):
        update_post_url = f"{self.BASE_URI_PATH}/posts/nonexistent-slug"
        data = {
            "title": "Updated Test Post",
            "text": "This is updated test post content",
        }

        response = await aclient.put(
            update_post_url,
            data=data,
            headers={"Authorization": f"Bearer {self.auth_token}"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["status"], "failure")
        self.assertEqual(response.data["message"], "Post not found")

    async def test_update_post_unauthorized_user(self):
        update_post_url = f"{self.BASE_URI_PATH}/posts/{self.sample_post.slug}"
        data = {
            "title": "Updated Test Post",
            "text": "This is updated test post content",
        }

        response = await aclient.put(
            update_post_url,
            data=data,
            headers={"Authorization": f"Bearer {self.other_auth_token}"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["status"], "failure")
        self.assertEqual(response.data["code"], ErrorCode.INVALID_OWNER)
        self.assertEqual(
            response.data["message"], "You are not authorized to update this post"
        )

    async def test_update_post_no_auth(self):
        update_post_url = f"{self.BASE_URI_PATH}/posts/{self.sample_post.slug}"
        data = {
            "title": "Updated Test Post",
            "text": "This is updated test post content",
        }

        response = await aclient.put(update_post_url, data=data)
        self.assertEqual(response.status_code, 401)

    # TEST POSSIBLE RESPONSES FOR DELETE POST ENDPOINT
    async def test_delete_post_successful(self):
        delete_post_url = f"{self.BASE_URI_PATH}/posts/{self.sample_post.slug}"

        response = await aclient.delete(
            delete_post_url, headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Post deleted successfully")

    async def test_delete_post_not_found(self):
        delete_post_url = f"{self.BASE_URI_PATH}/posts/nonexistent-slug"

        response = await aclient.delete(
            delete_post_url, headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["status"], "failure")
        self.assertEqual(response.data["message"], "Post not found")

    async def test_delete_post_unauthorized_user(self):
        delete_post_url = f"{self.BASE_URI_PATH}/posts/{self.sample_post.slug}"

        response = await aclient.delete(
            delete_post_url,
            headers={"Authorization": f"Bearer {self.other_auth_token}"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["status"], "failure")
        self.assertEqual(response.data["code"], ErrorCode.INVALID_OWNER)
        self.assertEqual(
            response.data["message"], "You are not authorized to delete this post"
        )

    async def test_delete_post_no_auth(self):
        delete_post_url = f"{self.BASE_URI_PATH}/posts/{self.sample_post.slug}"

        response = await aclient.delete(delete_post_url)
        self.assertEqual(response.status_code, 401)


@pytest.mark.django_db
class TestBlogCommentsEndpoints(TestCase):
    BASE_URI_PATH = "/api/v1/blog"

    def setUp(self):
        self.author = TestAccountsUtil.first_verified_user()
        self.other_user = TestAccountsUtil.second_verified_user()
        self.auth_token = TestAccountsUtil.auth_token(self.author)
        self.other_auth_token = TestAccountsUtil.auth_token(self.other_user)
        self.sample_post = TestBlogUtil.sample_post(self.author)
        self.sample_comment = TestBlogUtil.sample_comment(self.author, self.sample_post)

    # TEST POSSIBLE RESPONSES FOR GET POST COMMENTS ENDPOINT
    async def test_get_post_comments_successful(self):
        get_comments_url = f"{self.BASE_URI_PATH}/posts/{self.sample_post.slug}/comments?page=1&limit=10"

        response = await aclient.get(get_comments_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Comments returned successfully")
        self.assertIn("data", response.data)

    async def test_get_post_comments_with_sort_asc(self):
        get_comments_url = f"{self.BASE_URI_PATH}/posts/{self.sample_post.slug}/comments?page=1&limit=10&sort=asc"

        response = await aclient.get(get_comments_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Comments returned successfully")

    async def test_get_post_comments_with_sort_desc(self):
        get_comments_url = f"{self.BASE_URI_PATH}/posts/{self.sample_post.slug}/comments?page=1&limit=10&sort=desc"

        response = await aclient.get(get_comments_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Comments returned successfully")

    async def test_get_post_comments_invalid_sort(self):
        get_comments_url = f"{self.BASE_URI_PATH}/posts/{self.sample_post.slug}/comments?page=1&limit=10&sort=invalid"

        response = await aclient.get(get_comments_url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["status"], "failure")
        self.assertEqual(response.data["code"], ErrorCode.INVALID_QUERY_PARAM)
        self.assertEqual(
            response.data["message"], "Sort must be either 'asc' or 'desc'"
        )

    async def test_get_post_comments_post_not_found(self):
        get_comments_url = (
            f"{self.BASE_URI_PATH}/posts/nonexistent-slug/comments?page=1&limit=10"
        )

        response = await aclient.get(get_comments_url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["status"], "failure")
        self.assertEqual(response.data["message"], "Post not found")

    # TEST POSSIBLE RESPONSES FOR CREATE COMMENT ENDPOINT
    async def test_create_comment_successful(self):
        create_comment_url = (
            f"{self.BASE_URI_PATH}/posts/{self.sample_post.slug}/comments"
        )
        data = {"text": "This is a new test comment"}

        response = await aclient.post(
            create_comment_url,
            json.dumps(data),
            headers={"Authorization": f"Bearer {self.auth_token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Comment created successfully")
        self.assertIn("data", response.data)

    async def test_create_comment_post_not_found(self):
        create_comment_url = f"{self.BASE_URI_PATH}/posts/nonexistent-slug/comments"
        data = {"text": "This is a new test comment"}

        response = await aclient.post(
            create_comment_url,
            json.dumps(data),
            headers={"Authorization": f"Bearer {self.auth_token}"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["status"], "failure")
        self.assertEqual(response.data["message"], "Post not found")

    async def test_create_comment_no_auth(self):
        create_comment_url = (
            f"{self.BASE_URI_PATH}/posts/{self.sample_post.slug}/comments"
        )
        data = {"text": "This is a new test comment"}

        response = await aclient.post(create_comment_url, json.dumps(data))
        self.assertEqual(response.status_code, 401)

    # TEST POSSIBLE RESPONSES FOR GET SINGLE COMMENT ENDPOINT
    async def test_get_single_comment_successful(self):
        get_comment_url = f"{self.BASE_URI_PATH}/comments/{self.sample_comment.id}"

        response = await aclient.get(get_comment_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Comment returned successfully")
        self.assertIn("data", response.data)

    async def test_get_single_comment_not_found(self):
        fake_uuid = str(uuid.uuid4())
        get_comment_url = f"{self.BASE_URI_PATH}/comments/{fake_uuid}"

        response = await aclient.get(get_comment_url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["status"], "failure")
        self.assertEqual(response.data["message"], "Comment not found")

    # TEST POSSIBLE RESPONSES FOR UPDATE COMMENT ENDPOINT
    async def test_update_comment_successful(self):
        update_comment_url = f"{self.BASE_URI_PATH}/comments/{self.sample_comment.id}"
        data = {"text": "Updated comment text"}

        response = await aclient.put(
            update_comment_url,
            json.dumps(data),
            headers={"Authorization": f"Bearer {self.auth_token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Comment updated successfully")
        self.assertIn("data", response.data)

    async def test_update_comment_not_found(self):
        fake_uuid = str(uuid.uuid4())
        update_comment_url = f"{self.BASE_URI_PATH}/comments/{fake_uuid}"
        data = {"text": "Updated comment text"}

        response = await aclient.put(
            update_comment_url,
            json.dumps(data),
            headers={"Authorization": f"Bearer {self.auth_token}"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["status"], "failure")
        self.assertEqual(response.data["message"], "Comment not found")

    async def test_update_comment_unauthorized_user(self):
        update_comment_url = f"{self.BASE_URI_PATH}/comments/{self.sample_comment.id}"
        data = {"text": "Updated comment text"}

        response = await aclient.put(
            update_comment_url,
            json.dumps(data),
            headers={"Authorization": f"Bearer {self.other_auth_token}"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["status"], "failure")
        self.assertEqual(response.data["code"], ErrorCode.INVALID_OWNER)
        self.assertEqual(
            response.data["message"], "You are not authorized to update this comment"
        )

    async def test_update_comment_no_auth(self):
        update_comment_url = f"{self.BASE_URI_PATH}/comments/{self.sample_comment.id}"
        data = {"text": "Updated comment text"}

        response = await aclient.put(update_comment_url, json.dumps(data))
        self.assertEqual(response.status_code, 401)

    # TEST POSSIBLE RESPONSES FOR DELETE COMMENT ENDPOINT
    async def test_delete_comment_successful(self):
        delete_comment_url = f"{self.BASE_URI_PATH}/comments/{self.sample_comment.id}"

        response = await aclient.delete(
            delete_comment_url, headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Comment deleted successfully")

    async def test_delete_comment_not_found(self):
        fake_uuid = str(uuid.uuid4())
        delete_comment_url = f"{self.BASE_URI_PATH}/comments/{fake_uuid}"

        response = await aclient.delete(
            delete_comment_url, headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["status"], "failure")
        self.assertEqual(response.data["message"], "Comment not found")

    async def test_delete_comment_unauthorized_user(self):
        delete_comment_url = f"{self.BASE_URI_PATH}/comments/{self.sample_comment.id}"

        response = await aclient.delete(
            delete_comment_url,
            headers={"Authorization": f"Bearer {self.other_auth_token}"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["status"], "failure")
        self.assertEqual(response.data["code"], ErrorCode.INVALID_OWNER)
        self.assertEqual(
            response.data["message"], "You are not authorized to update this comment"
        )

    async def test_delete_comment_no_auth(self):
        delete_comment_url = f"{self.BASE_URI_PATH}/comments/{self.sample_comment.id}"

        response = await aclient.delete(delete_comment_url)
        self.assertEqual(response.status_code, 401)


@pytest.mark.django_db
class TestBlogRepliesEndpoints(TestCase):
    BASE_URI_PATH = "/api/v1/blog"

    def setUp(self):
        self.author = TestAccountsUtil.first_verified_user()
        self.other_user = TestAccountsUtil.second_verified_user()
        self.auth_token = TestAccountsUtil.auth_token(self.author)
        self.other_auth_token = TestAccountsUtil.auth_token(self.other_user)
        self.sample_post = TestBlogUtil.sample_post(self.author)
        self.sample_comment = TestBlogUtil.sample_comment(self.author, self.sample_post)
        self.sample_reply = TestBlogUtil.sample_reply(
            self.author, self.sample_post, self.sample_comment
        )

    # TEST POSSIBLE RESPONSES FOR GET COMMENT REPLIES ENDPOINT
    async def test_get_comment_replies_successful(self):
        get_replies_url = f"{self.BASE_URI_PATH}/comments/{self.sample_comment.id}/replies?page=1&limit=10"

        response = await aclient.get(get_replies_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Replies returned successfully")
        self.assertIn("data", response.data)

    async def test_get_comment_replies_invalid_sort(self):
        get_replies_url = f"{self.BASE_URI_PATH}/comments/{self.sample_comment.id}/replies?page=1&limit=10&sort=invalid"

        response = await aclient.get(get_replies_url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["status"], "failure")
        self.assertEqual(response.data["code"], ErrorCode.INVALID_QUERY_PARAM)
        self.assertEqual(
            response.data["message"], "Sort must be either 'asc' or 'desc'"
        )

    async def test_get_comment_replies_comment_not_found(self):
        fake_uuid = str(uuid.uuid4())
        get_replies_url = (
            f"{self.BASE_URI_PATH}/comments/{fake_uuid}/replies?page=1&limit=10"
        )

        response = await aclient.get(get_replies_url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["status"], "failure")
        self.assertEqual(response.data["message"], "Comment not found")

    # TEST POSSIBLE RESPONSES FOR CREATE REPLY ENDPOINT
    async def test_create_reply_successful(self):
        create_reply_url = (
            f"{self.BASE_URI_PATH}/comments/{self.sample_comment.id}/replies"
        )
        data = {"text": "This is a new test reply"}

        response = await aclient.post(
            create_reply_url,
            json.dumps(data),
            headers={"Authorization": f"Bearer {self.auth_token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Reply created successfully")
        self.assertIn("data", response.data)

    async def test_create_reply_comment_not_found(self):
        fake_uuid = str(uuid.uuid4())
        create_reply_url = f"{self.BASE_URI_PATH}/comments/{fake_uuid}/replies"
        data = {"text": "This is a new test reply"}

        response = await aclient.post(
            create_reply_url,
            json.dumps(data),
            headers={"Authorization": f"Bearer {self.auth_token}"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["status"], "failure")
        self.assertEqual(response.data["message"], "Comment not found")

    async def test_create_reply_no_auth(self):
        create_reply_url = (
            f"{self.BASE_URI_PATH}/comments/{self.sample_comment.id}/replies"
        )
        data = {"text": "This is a new test reply"}

        response = await aclient.post(create_reply_url, json.dumps(data))
        self.assertEqual(response.status_code, 401)

    # TEST POSSIBLE RESPONSES FOR GET SINGLE REPLY ENDPOINT
    async def test_get_single_reply_successful(self):
        get_reply_url = f"{self.BASE_URI_PATH}/replies/{self.sample_reply.id}"

        response = await aclient.get(get_reply_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Reply returned successfully")
        self.assertIn("data", response.data)

    async def test_get_single_reply_not_found(self):
        fake_uuid = str(uuid.uuid4())
        get_reply_url = f"{self.BASE_URI_PATH}/replies/{fake_uuid}"

        response = await aclient.get(get_reply_url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["status"], "failure")
        self.assertEqual(response.data["message"], "Reply not found")

    # TEST POSSIBLE RESPONSES FOR UPDATE REPLY ENDPOINT
    async def test_update_reply_successful(self):
        update_reply_url = f"{self.BASE_URI_PATH}/replies/{self.sample_reply.id}"
        data = {"text": "Updated reply text"}

        response = await aclient.put(
            update_reply_url,
            json.dumps(data),
            headers={"Authorization": f"Bearer {self.auth_token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Reply updated successfully")
        self.assertIn("data", response.data)

    async def test_update_reply_not_found(self):
        fake_uuid = str(uuid.uuid4())
        update_reply_url = f"{self.BASE_URI_PATH}/replies/{fake_uuid}"
        data = {"text": "Updated reply text"}

        response = await aclient.put(
            update_reply_url,
            json.dumps(data),
            headers={"Authorization": f"Bearer {self.auth_token}"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["status"], "failure")
        self.assertEqual(response.data["message"], "Reply not found")

    async def test_update_reply_unauthorized_user(self):
        update_reply_url = f"{self.BASE_URI_PATH}/replies/{self.sample_reply.id}"
        data = {"text": "Updated reply text"}

        response = await aclient.put(
            update_reply_url,
            json.dumps(data),
            headers={"Authorization": f"Bearer {self.other_auth_token}"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["status"], "failure")
        self.assertEqual(response.data["code"], ErrorCode.INVALID_OWNER)
        self.assertEqual(
            response.data["message"], "You are not authorized to update this reply"
        )

    async def test_update_reply_no_auth(self):
        update_reply_url = f"{self.BASE_URI_PATH}/replies/{self.sample_reply.id}"
        data = {"text": "Updated reply text"}

        response = await aclient.put(update_reply_url, json.dumps(data))
        self.assertEqual(response.status_code, 401)

    # TEST POSSIBLE RESPONSES FOR DELETE REPLY ENDPOINT
    async def test_delete_reply_successful(self):
        delete_reply_url = f"{self.BASE_URI_PATH}/replies/{self.sample_reply.id}"

        response = await aclient.delete(
            delete_reply_url, headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Reply deleted successfully")

    async def test_delete_reply_not_found(self):
        fake_uuid = str(uuid.uuid4())
        delete_reply_url = f"{self.BASE_URI_PATH}/replies/{fake_uuid}"

        response = await aclient.delete(
            delete_reply_url, headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["status"], "failure")
        self.assertEqual(response.data["message"], "Reply not found")

    async def test_delete_reply_unauthorized_user(self):
        delete_reply_url = f"{self.BASE_URI_PATH}/replies/{self.sample_reply.id}"

        response = await aclient.delete(
            delete_reply_url,
            headers={"Authorization": f"Bearer {self.other_auth_token}"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["status"], "failure")
        self.assertEqual(response.data["code"], ErrorCode.INVALID_OWNER)
        self.assertEqual(
            response.data["message"], "You are not authorized to update this reply"
        )

    async def test_delete_reply_no_auth(self):
        delete_reply_url = f"{self.BASE_URI_PATH}/replies/{self.sample_reply.id}"

        response = await aclient.delete(delete_reply_url)
        self.assertEqual(response.status_code, 401)


@pytest.mark.django_db
class TestBlogLikesEndpoints(TestCase):
    BASE_URI_PATH = "/api/v1/blog"

    def setUp(self):
        self.author = TestAccountsUtil.first_verified_user()
        self.other_user = TestAccountsUtil.second_verified_user()
        self.auth_token = TestAccountsUtil.auth_token(self.author)
        self.other_auth_token = TestAccountsUtil.auth_token(self.other_user)
        self.sample_post = TestBlogUtil.sample_post(self.author)
        self.sample_comment = TestBlogUtil.sample_comment(self.author, self.sample_post)
        self.sample_reply = TestBlogUtil.sample_reply(
            self.author, self.sample_post, self.sample_comment
        )

    # TEST POSSIBLE RESPONSES FOR GET LIKES ENDPOINT
    async def test_get_post_likes_successful(self):
        get_likes_url = f"{self.BASE_URI_PATH}/likes/{self.sample_post.id}?page=1&limit=10&data_type=post"

        response = await aclient.get(get_likes_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(
            response.data["message"], "Likes/Dislikes returned successfully"
        )
        self.assertIn("data", response.data)

    async def test_get_comment_likes_successful(self):
        get_likes_url = f"{self.BASE_URI_PATH}/likes/{self.sample_comment.id}?page=1&limit=10&data_type=comment"

        response = await aclient.get(get_likes_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(
            response.data["message"], "Likes/Dislikes returned successfully"
        )
        self.assertIn("data", response.data)

    async def test_get_reply_likes_successful(self):
        get_likes_url = f"{self.BASE_URI_PATH}/likes/{self.sample_reply.id}?page=1&limit=10&data_type=reply"

        response = await aclient.get(get_likes_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(
            response.data["message"], "Likes/Dislikes returned successfully"
        )
        self.assertIn("data", response.data)

    async def test_get_dislikes_successful(self):
        get_dislikes_url = f"{self.BASE_URI_PATH}/likes/{self.sample_post.id}?page=1&limit=10&data_type=post&is_dislike=true"

        response = await aclient.get(get_dislikes_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(
            response.data["message"], "Likes/Dislikes returned successfully"
        )
        self.assertIn("data", response.data)

    async def test_get_likes_invalid_data_type(self):
        get_likes_url = f"{self.BASE_URI_PATH}/likes/{self.sample_post.id}?page=1&limit=10&data_type=invalid"

        response = await aclient.get(get_likes_url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["status"], "failure")
        self.assertEqual(response.data["code"], ErrorCode.INVALID_QUERY_PARAM)
        self.assertEqual(
            response.data["message"],
            "data_type must be either 'post', 'comment' or 'reply'",
        )

    async def test_get_likes_object_not_found(self):
        fake_uuid = str(uuid.uuid4())
        get_likes_url = (
            f"{self.BASE_URI_PATH}/likes/{fake_uuid}?page=1&limit=10&data_type=post"
        )

        response = await aclient.get(get_likes_url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["status"], "failure")
        self.assertEqual(response.data["message"], "Post not found")

    # TEST POSSIBLE RESPONSES FOR LIKE/DISLIKE TOGGLE ENDPOINT
    async def test_like_post_successful(self):
        toggle_like_url = f"{self.BASE_URI_PATH}/likes/{self.sample_post.id}/toggle?data_type=post&is_dislike=false"

        response = await aclient.get(
            toggle_like_url, headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Like added successfully")

    async def test_dislike_post_successful(self):
        toggle_dislike_url = f"{self.BASE_URI_PATH}/likes/{self.sample_post.id}/toggle?data_type=post&is_dislike=true"

        response = await aclient.get(
            toggle_dislike_url, headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Dislike added successfully")

    async def test_like_comment_successful(self):
        toggle_like_url = f"{self.BASE_URI_PATH}/likes/{self.sample_comment.id}/toggle?data_type=comment&is_dislike=false"

        response = await aclient.get(
            toggle_like_url, headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Like added successfully")

    async def test_like_reply_successful(self):
        toggle_like_url = f"{self.BASE_URI_PATH}/likes/{self.sample_reply.id}/toggle?data_type=reply&is_dislike=false"

        response = await aclient.get(
            toggle_like_url, headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Like added successfully")

    async def test_toggle_like_invalid_data_type(self):
        toggle_like_url = (
            f"{self.BASE_URI_PATH}/likes/{self.sample_post.id}/toggle?data_type=invalid"
        )

        response = await aclient.get(
            toggle_like_url, headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["status"], "failure")
        self.assertEqual(response.data["code"], ErrorCode.INVALID_QUERY_PARAM)
        self.assertEqual(
            response.data["message"],
            "data_type must be either 'post', 'comment' or 'reply'",
        )

    async def test_toggle_like_object_not_found(self):
        fake_uuid = str(uuid.uuid4())
        toggle_like_url = (
            f"{self.BASE_URI_PATH}/likes/{fake_uuid}/toggle?data_type=post"
        )

        response = await aclient.get(
            toggle_like_url, headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["status"], "failure")
        self.assertEqual(response.data["message"], "Post not found")

    async def test_toggle_like_no_auth(self):
        toggle_like_url = (
            f"{self.BASE_URI_PATH}/likes/{self.sample_post.id}/toggle?data_type=post"
        )

        response = await aclient.get(toggle_like_url)
        self.assertEqual(response.status_code, 401)

    async def test_remove_like_by_toggling_again(self):
        # First, add a like
        await Like.objects.acreate(
            author=self.author, post=self.sample_post, is_disliked=False
        )

        toggle_like_url = f"{self.BASE_URI_PATH}/likes/{self.sample_post.id}/toggle?data_type=post&is_dislike=false"

        response = await aclient.get(
            toggle_like_url, headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Like removed successfully")

    async def test_switch_like_to_dislike(self):
        # First, add a like
        await Like.objects.acreate(
            author=self.author, post=self.sample_post, is_disliked=False
        )

        toggle_dislike_url = f"{self.BASE_URI_PATH}/likes/{self.sample_post.id}/toggle?data_type=post&is_dislike=true"

        response = await aclient.get(
            toggle_dislike_url, headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Dislike updated successfully")
