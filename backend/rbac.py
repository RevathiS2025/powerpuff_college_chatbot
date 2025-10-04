from enum import Enum

class UserRole(Enum):
    """
    Defines the user roles within the system.
    Using an Enum makes role comparisons and assignments safer and more explicit.
    """
    PARENT = "parent"
    STUDENT = "student"
    PROFESSOR = "professor"
    DEAN = "dean"
    # Add other roles here if needed in the future

    @classmethod
    def get_all_roles(cls) -> list[str]:
        """
        Returns a list of all defined role values.
        Useful for populating UI elements like signup dropdowns.
        """
        return [role.value for role in cls]

    @classmethod
    def is_valid_role(cls, role_str: str) -> bool:
        """
        Checks if a given string corresponds to a valid user role.
        """
        return role_str in cls.get_all_roles()

# --- Optional: Define Role Hierarchies ---
# This dictionary can be used for more complex permission checks,
# for instance, allowing a 'dean' to access everything a 'professor' can.
ROLE_HIERARCHY = {
    UserRole.DEAN.value: [
        UserRole.DEAN.value, 
        UserRole.PROFESSOR.value, 
        UserRole.STUDENT.value, 
        UserRole.PARENT.value
    ],
    UserRole.PROFESSOR.value: [
        UserRole.PROFESSOR.value
    ],
    UserRole.STUDENT.value: [
        UserRole.STUDENT.value
    ],
    UserRole.PARENT.value: [
        UserRole.PARENT.value
    ]
}

def get_accessible_roles(user_role: str) -> list[str]:
    """
    Given a user's primary role, return all roles they have access to
    based on the defined hierarchy.
    
    For the current ChromaDB filter, this isn't strictly necessary as we filter
    by the primary role, but it's essential for more advanced RBAC systems.
    
    Args:
        user_role (str): The primary role of the user.

    Returns:
        list[str]: A list of all roles the user can access content from.
    """
    if not UserRole.is_valid_role(user_role):
        return []
    return ROLE_HIERARCHY.get(user_role, [])


# --- Example Usage ---
# This block demonstrates how the functions in this module work.
if __name__ == '__main__':
    print("--- RBAC Module Test ---")

    # Get all roles for a signup form
    all_roles = UserRole.get_all_roles()
    print(f"All available roles: {all_roles}")

    # Validate roles
    print(f"Is 'student' a valid role? {UserRole.is_valid_role('student')}")
    print(f"Is 'admin' a valid role? {UserRole.is_valid_role('admin')}")

    # Test role hierarchy
    dean_permissions = get_accessible_roles('dean')
    print(f"A 'dean' can access content for roles: {dean_permissions}")

    student_permissions = get_accessible_roles('student')
    print(f"A 'student' can access content for roles: {student_permissions}")
