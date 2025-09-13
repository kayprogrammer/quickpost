from django.contrib import admin

from apps.blog.models import Comment, Like, Post

class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "title")
    list_filter = ("title",)
    search_fields = ("author__first_name", "author__last_name", "title", "text")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "text")
    list_filter = ("author",)
    search_fields = ("author__first_name", "author__last_name", "parent__text", "text")


class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "is_disliked")
    list_filter = ("author", "is_disliked")
    search_fields = (
        "author__first_name",
        "author__last_name",
        "post__title",
        "comment__text",
    )


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Like, LikeAdmin)
