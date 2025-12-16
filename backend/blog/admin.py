from django.contrib import admin
from .models import Post, Media, Tag, Comment
from django.utils import timezone
import jdatetime

# ================= Post =================
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'tags', 'author')
    search_fields = ('title', 'content', 'author__username')
    autocomplete_fields = ('tags', 'likes', 'author')
    readonly_fields = ('slug', 'created_at', 'updated_at', )


# ================= Media =================
@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('file', 'author')
    list_filter = ('author',)
    search_fields = ('file', 'author__username')
    autocomplete_fields = ('author',)

# ================= Tag =================
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# ================= Comment =================
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('short_content', 'post', 'author', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'author', 'post')
    search_fields = ('content', 'author__username', 'post__title')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('author', 'post')

    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = "متن دیدگاه"


