def perform_subscribe_or_unsubscribe(publisher, user, action) -> None:
    """
    Subscribe or unsubscribe a user to/from a Publisher based on their role.

    This function handles role-based subscriptions:
        - Readers → publisher.readers
        - Journalists → publisher.journalists
        - Editors → publisher.editors

    Actions:
        - "subscribe": Adds the user to the publisher M2M field.
        - "unsubscribe": Removes the user from the publisher M2M field.

    :param publisher: The Publisher instance to modify.
    :type publisher: Publisher
    :param user: The User performing the subscription action.
    :type user: User
    :param action: Either "subscribe" or "unsubscribe".
    :type action: str
    :raises ValueError: If `action` or `user.role` is invalid.
    """
    if action == "subscribe":
        if user.role == "Reader":
            publisher.readers.add(user)
        elif user.role == "Journalist":
            publisher.journalists.add(user)
        elif user.role == "Editor":
            publisher.editors.add(user)

    elif action == "unsubscribe":
        if user.role == "Reader":
            publisher.readers.remove(user)
        elif user.role == "Journalist":
            publisher.journalists.remove(user)
        elif user.role == "Editor":
            publisher.editors.remove(user)
