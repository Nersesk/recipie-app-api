"""
Serializers for recipie APIs
"""
from core.models import Recipie, Tag
from rest_framework.serializers import ModelSerializer


class TagSerializer(ModelSerializer):
    """Serializer for Tags"""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id', ]


class RecipeSerializer(ModelSerializer):
    """Serializer for recipies"""
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipie
        fields = ('id', 'title', 'time_minutes', 'price', 'link', 'tags')
        read_only_fields = ('id',)
    def _get_or_create_tags(self, tags, recipie):
        """Handle getting or creating tags"""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipie.tags.add(tag_obj)

    def create(self, validated_data):
        """Create a recipe."""
        tags = validated_data.pop('tags', [])
        recipe = Recipie.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Update recipe."""
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
class RecipieDetailSerializer(RecipeSerializer):
    """Serializer for recipe details view."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ('description',)
