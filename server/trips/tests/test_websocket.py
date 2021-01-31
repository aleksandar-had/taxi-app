import pytest
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import Group


from taxi.routing import application


@database_sync_to_async
def create_user(
        username,
        password,
        group="rider"
):
    user = get_user_model().objects.create_user(
        username=username,
        password=password
    )
    user_group, _ = Group.objects.get_or_create(name=group)
    user.groups.add(user_group)
    user.save()
    access = AccessToken.for_user(user)
    return user, access


TEST_CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestWebSocket:

    async def test_can_connect_to_server(self, settings):
        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS
        _, access = await create_user(
            "user@example.com", "pAssw0rd!"
        )
        communicator = WebsocketCommunicator(
            application=application,
            path=f"/taxi/?token={access}"
        )
        connected, _ = await communicator.connect()
        assert connected is True
        await communicator.disconnect()

    async def test_can_send_and_receive_messages(self, settings):
        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS
        _, access = await create_user(
            "user@example.com", "pAssw0rd!"
        )
        communicator = WebsocketCommunicator(
            application=application,
            path=f"/taxi/?token={access}"
        )
        connected, _ = await communicator.connect()
        message = {
            "type": "echo.message",
            "data": "Test message.",
        }
        await communicator.send_json_to(message)
        response = await communicator.receive_json_from()
        assert response == message
        await communicator.disconnect()

    async def test_cannot_connect_to_socket(self, settings):
        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS
        communicator = WebsocketCommunicator(
            application=application,
            path="/taxi/"
        )
        connected, _ = await communicator.connect()
        assert connected is False
        await communicator.disconnect()

    async def test_join_driver_pool(self, settings):
        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS
        _, access = await create_user(
            "user@example.com",
            "pAssw0rd!",
            "driver"
        )
        communicator = WebsocketCommunicator(
            application=application,
            path=f"/taxi/?token={access}"
        )
        connected, _ = await communicator.connect()
        message = {
            "type": "echo.message",
            "data": "Test message."
        }
        channel_layer = get_channel_layer()
        await channel_layer.group_send("drivers", message=message)
        response = await communicator.receive_json_from()
        assert response == message
        await communicator.disconnect()

    async def test_request_trip(self, settings):
        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS
        user, access = await create_user(
            "user@example.com",
            "pAssw0rd!",
            "rider"
        )
        communicator = WebsocketCommunicator(
            application=application,
            path=f"/taxi/?token={access}"
        )
        connected, _ = await communicator.connect()
        await communicator.send_json_to(
            {
                "type": "create.trip",
                "data": {
                    "pick_up_address": "Stephansplatz 1",
                    "drop_off_address": "Georgi S. Rakovski 108",
                    "rider": user.id
                }
            }
        )
        response = await communicator.receive_json_from()
        response_data = response.get("data")
        assert response_data["id"] is not None
        assert response_data["pick_up_address"] == "Stephansplatz 1"
        assert response_data["drop_off_address"] == "Georgi S. Rakovski 108"
        assert response_data["rider"]["username"] == user.username
        assert response_data["status"] == "REQUESTED"
        assert response_data["driver"] is None
        await communicator.disconnect()

    async def test_driver_alerted_on_request(self, settings):
        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

        # Drivers' group test channel
        channel_layer = get_channel_layer()
        await channel_layer.group_add(
            group="drivers",
            channel="test_channel"
        )
        user, access = await create_user(
            "user@example.com",
            "pAssw0rd!",
            "rider"
        )
        communicator = WebsocketCommunicator(
            application=application,
            path=f"/taxi/?token={access}",
        )
        connected, _ = await communicator.connect()
        await communicator.send_json_to(
            {
                "type": "create.trip",
                "data": {
                    "pick_up_address": "Stephansplatz 1",
                    "drop_off_address": "Georgi S. Rakovski 108",
                    "rider": user.id
                }

            }
        )
        response = await communicator.receive_json_from()
        response_data = response.get("data")
        assert response_data["id"] is not None
        assert response_data["rider"]["username"] == user.username
        assert response_data["driver"] is None
        await communicator.disconnect()
