from src.models import FavoritesORM, PlaylistORM, PlaylistItemORM
from src.repositories.mappers.base import DataMapper
from src.models.users import UserORM, FriendshipORM
from src.schemas.favorites import FavoriteDTO
from src.schemas.friendship import FriendshipDTO
from src.schemas.playlists import PlaylistDTO, PlaylistWithRelsDTO, PlaylistItemDTO
from src.schemas.users import UserDTO, DBUserDTO


class UserDataMapper(DataMapper):
    db_model = UserORM
    schema = UserDTO


class DBUserDataMapper(DataMapper):
    db_model = UserORM
    schema = DBUserDTO


class FavoritesDataMapper(DataMapper):
    db_model = FavoritesORM
    schema = FavoriteDTO


class FriendshipDataMapper(DataMapper):
    db_model = FriendshipORM
    schema = FriendshipDTO


class PlaylistDataMapper(DataMapper):
    db_model = PlaylistORM
    schema = PlaylistDTO


class PlaylistWithRelsDataMapper(DataMapper):
    db_model = PlaylistORM
    schema = PlaylistWithRelsDTO


class PlaylistItemDataMapper(DataMapper):
    db_model = PlaylistItemORM
    schema = PlaylistItemDTO
