from django.db import transaction
from rest_framework import serializers

from core.models import User
from goals.models.board import Board, BoardParticipant


# ----------------------------------------------------------------------------------------------------------------------
# Create serializers
class BoardParticipantSerializer(serializers.ModelSerializer):
    """Serializer for participants"""
    role = serializers.ChoiceField(required=True, choices=BoardParticipant.Role.choices[1:])
    user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        model = BoardParticipant
        fields = '__all__'
        read_only_fields: tuple[str] = ('id', 'created', 'updated', 'board')


# ----------------------------------------------------------------
class BoardCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new board"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Board
        fields = '__all__'
        read_only_fields: tuple[str] = ('id', 'created', 'updated')

    def create(self, validated_data: dict) -> Board:
        """Create a new board and add the current user as an owner"""
        user = validated_data.pop('user')
        board: Board = Board.objects.create(**validated_data)

        BoardParticipant.objects.create(
            user=user,
            board=board,
            role=BoardParticipant.Role.owner)

        return board


# ----------------------------------------------------------------
class BoardListSerializer(serializers.ModelSerializer):
    """Serializer for listing boards"""

    class Meta:
        model = Board
        fields = '__all__'


# ----------------------------------------------------------------
class BoardSerializer(serializers.ModelSerializer):
    """Serializer for retrieving/updating/deleting board"""
    participants = BoardParticipantSerializer(many=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Board
        fields = '__all__'
        read_only_fields: tuple[str] = ('id', 'created', 'updated')

    def update(self, board: Board, validated_data: dict) -> Board:
        """Update a board with new data and create/delete participants"""
        # Extract required data from validated_data
        owner = validated_data.pop('user')
        new_participants = validated_data.pop('participants')
        new_by_id: dict = {participant['user'].id: participant for participant in new_participants}

        # Delete participants who are not in new_participants or set a different role
        old_participants = board.participants.exclude(user=owner)
        with transaction.atomic():
            for old_participant in old_participants:
                if old_participant.user_id not in new_by_id:
                    old_participant.delete()

                elif old_participant.role != new_by_id[old_participant.user_id]['role']:
                    old_participant.role = new_by_id[old_participant.user_id]['role']
                    old_participant.save()

                new_by_id.pop(old_participant.user_id)

            # Create new participants
            for new_participant in new_by_id.values():
                BoardParticipant.objects.create(
                    board=board,
                    user=new_participant['user'],
                    role=new_participant['role'])

            # Update board with new data
            board.title = validated_data['title']
            board.save()

        return board
