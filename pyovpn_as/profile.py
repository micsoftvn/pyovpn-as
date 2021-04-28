"""Contains the classes which represents profiles on the server.

Some notes on profiles:

* If you want to make a group, you can't just pass ``type='group'``, you also have to declare ``group_declare='true'``
"""
from typing import Any

from . import exceptions


class Profile:
    """Represents a profile on the OpenVPN Access Server and provides a logical
    layer to extract meaning from the properties set on the profiles.

    The profile doesn't have to exist on the server for this class to be 
    instantiated, and can be passed as an argument to functions manipulating 
    users, groups, and profiles.

    This class exists primarily as a superclass to User and Group

    Args:
        **attrs (dict[str, Any]): The dictionary containing the attributes for a
            profile. This can be fetched from the server with RemoteSacli
            UserPropGet

    Attributes:
        _attrs (dict[str, Any]): The dictionary containing the attributes for a
            profile provided at ``__init__``
        USER_CONNECT (str): value of ``type`` equal to a profile that is
            evaluated only when a user connects
        USER_CONNECT_HIDDEN (str): value of ``type`` when a profile is
            evaluated the same as USER_CONNECT but is hidden from the admin UI
        USER_COMPILE (str): value of ``type`` when a profile is evaluated on
            iptables compile or when a user connects
        USER_DEFAULT (str): value of ``type`` for the ``__DEFAULT__`` record
        GROUP (str): value of ``type`` for group records
        PROFILE_TYPES (tuple[str]): All types that a profile could be
        USER_TYPES (tuple[str]): List of types valid for a new user
    """
    USER_CONNECT = 'user_connect'
    USER_CONNECT_HIDDEN = 'user_connect_hidden'
    USER_COMPILE = 'user_compile'
    USER_DEFAULT = 'user_default'
    GROUP = 'group'

    PROFILE_TYPES = (
        USER_CONNECT, USER_CONNECT_HIDDEN, USER_COMPILE, USER_DEFAULT, GROUP
    )
    
    USER_TYPES = (
        USER_CONNECT, USER_CONNECT_HIDDEN, USER_COMPILE
    )

    def __init__(self, **attrs):
        for key in attrs:
            if not isinstance(key, str):
                raise TypeError(
                    'Attributes for a profile must have keys that are all '
                    'strings'
                )
        if attrs.get('type') not in self.PROFILE_TYPES:
            raise exceptions.AccessServerProfileIntegrityError(
                f"Value of property 'type' must be one of {self.PROFILE_TYPES}"
            )
        self._attrs = attrs
    

    @property
    def is_banned(self) -> bool:
        """bool: Whether or not the profile is banned.
        
        Derived from the ``prop_deny`` property.

        Default behaviour is False
        """
        prop = self._attrs.get('prop_deny', '')
        if not isinstance(prop, str):
            raise exceptions.AccessServerProfileIntegrityError(
                f'Type of prop_deny must be str, not a {type(prop)}'
            )
        return prop.lower() == 'true'
    
    
    @property
    def is_admin(self) -> bool:
        """bool: Whether or not the profile is a superuser/admin.
        
        Derived from the ``prop_superuser`` property.

        Default behaviour is False
        """
        prop = self._attrs.get('prop_superuser', '')
        if not isinstance(prop, str):
            raise exceptions.AccessServerProfileIntegrityError(
                f'Type of prop_superuser must be str, not a {type(prop)}'
            )
        return prop.lower() == 'true'
    

    @property
    def is_group(self) -> bool:
        """bool: Whether or not the profile represents a group. True when the 
        ``group_declare`` property is equal to true
        """
        prop = self._attrs.get('group_declare', '')
        if not isinstance(prop, str):
            raise exceptions.AccessServerProfileIntegrityError(
                f'Type of group_declare must be str, not a {type(prop)}'
            )
        return prop.lower() == 'true'


    @property
    def can_change_password(self) -> bool:
        """bool: Whether or not users derived from this profile can change
        their password via the web interface.
        
        Derived from the ``prop_pwd_change`` property.

        Default behaviour is False
        """
        prop = self._attrs.get('prop_pwd_change', '')
        if not isinstance(prop, str):
            raise exceptions.AccessServerProfileIntegrityError(
                f'Type of prop_pwd_change must be str, not a {type(prop)}'
            )
        return prop.lower() == 'true'


    @property
    def can_autologin(self) -> bool:
        """bool: Whether or not users derived from this profile can download a 
        connection profile which allows them to connect without a password.
        
        Derived from the ``prop_autologin`` property.

        Default behaviour is False
        """
        prop = self._attrs.get('prop_autologin', '')
        if not isinstance(prop, str):
            raise exceptions.AccessServerProfileIntegrityError(
                f'Type of prop_autologin must be str, not a {type(prop)}'
            )
        return prop.lower() == 'true'


    @property
    def will_check_password_strength(self) -> bool:
        """bool: Whether the server should check the password strength when a 
        user derived from this profile tries to change it.
        
        Derived from the ``prop_pwd_strength`` property.

        Default behaviour is True
        """
        prop = self._attrs.get('prop_pwd_strength', 'true')
        if not isinstance(prop, str):
            raise exceptions.AccessServerProfileIntegrityError(
                f'Type of prop_pwd_strength must be str, not a {type(prop)}'
            )
        return prop.lower() == 'true'


    @property
    def will_autogenerate_client(self) -> bool:
        """bool: Whether or not the server will autogenerate a connection 
        profile for users derived from this profile. If set to true and the 
        given user tries to access their client, the server will generate one 
        if it doesn't exist.
        
        Derived from the ``prop_autogenerate`` property.
        
        Default behaviour is True.
        """
        prop = self._attrs.get('prop_autogenerate', 'true')
        if not isinstance(prop, str):
            raise exceptions.AccessServerProfileIntegrityError(
                f'Type of prop_autogenerate must be str, not a {type(prop)}'
            )
        return prop.lower() == 'true'


    def get_prop(self, key: str) -> Any:
        """Get a property from the profile

        Args:
            key (str): The property key to get

        Returns:
            Any: The value at that key

        Raises:
            KeyError: No property defined for that key
        """
        value = self._attrs.get(
            key, KeyError(
                f"No value for key '{key}' defined."
            )
        )
        if isinstance(value, KeyError):
            raise value
        return value


    def __getattr__(self, attribute: str) -> Any:
        """If we can't get the attribute from regular means, this function is 
        called as a fallback

        In this case we try to fetch the attribute as though it were a property 
        of the profile we were searching for.

        Args:
            attribute (str): The attribute we are searching for

        Returns:
            Any: The value of the attribute from the properties of the profile

        Raises:
            AttributeError: When the property doesn't exist
        """
        value = self._attrs.get(
            attribute,
            AttributeError(
                f"'{self.__class__.__name__}' object has no attribute "
                f"'{attribute}'"
            )
        )
        if isinstance(value, AttributeError):
            raise value
        return value



class UserProfile(Profile):
    """Represents a user's profile on the server.

    This class encapsulates a user's profile on the server (whether or not it 
    exists or not) and provides a logical layer through which we can make sense 
    of a user's properties. This way, we are able to determine if a user is a 
    superuser by checking both their properties and the properties of the group 
    that they are a part of.

    Args:
        username (str): The name of the user whose profile we are representing
        **attrs (dict[str, Any]): The dictionary containing the attributes for a
            profile. This can be fetched from the server with RemoteSacli
            UserPropGet

    Attributes:
        username (str): The name of the user whose profile we are representing
        _attrs (dict[str, Any]): The dictionary containing the attributes for a
            profile provided at ``__init__``
    """
    def __init__(self, username: str, **attrs):
        if attrs.get('type') not in self.USER_TYPES:
            raise exceptions.AccessServerProfileIntegrityError(
                f"Value of type property must be one of {self.USER_TYPES} "
                "for a user profile"
            )
        super().__init__(**attrs)
        self.username = username



class GroupProfile(Profile):
    """Represents a group profile on the server

    This class encapsulates a group and its properties on the server (whether 
    it exists or not) and provides a logical layer through which we can make 
    sense of its properties. We also provide some assurance that the integrity 
    of the group's userprop profile is maintained.

    Args:
        group_name (str): The name of the group whose profile we are
            representing
        **attrs (dict[str, Any]): The dictionary containing the attributes for a
            profile. This can be fetched from the server with RemoteSacli
            UserPropGet

    Attributes:
        group_name (str): The name of the group whose profile we are
            representing
        _attrs (dict[str, Any]): The dictionary containing the attributes for a
            profile provided at ``__init__``
    """
    def __init__(self, group_name, **attrs):
        if attrs.get('type') != self.GROUP:
            raise exceptions.AccessServerProfileIntegrityError(
                f"Value of type for a group must be '{self.GROUP}'"
            )
        elif attrs.get('group_declare', '').lower() != 'true':
            raise exceptions.AccessServerProfileIntegrityError(
                'Value of group_declare must be true for a group'
            )
        super().__init__(**attrs)
        self.group_name = group_name
