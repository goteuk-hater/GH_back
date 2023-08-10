from rest_framework import serializers
from .models import *

class BookCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCategory
        fields = '__all__' 

class BookSerializer(serializers.ModelSerializer):
    book = BookCategorySerializer(many=True, read_only = True)
    
    class Meta:
        model = Book
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['category'] = CategoryRepresentationSerializer(read_only=True)
        return super(BookSerializer, self).to_representation(instance)

class CategoryRepresentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCategory
        fields = '__all__'