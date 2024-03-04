class UserRole():

    # const
    ADMIN_ROLE = 'admin'
    OPERATOR_ROLE = 'operator'
    USER_ROLE = 'user'
    ADMIN_ROLE_FRIENDLY = '管理者'
    OPERATOR_ROLE_FRIENDLY = '作業担当者'
    USER_ROLE_FRIENDLY = '申請者'

    @staticmethod
    def to_friendly(role):
        match role:
            case UserRole.ADMIN_ROLE:
                return UserRole.ADMIN_ROLE_FRIENDLY
            case UserRole.OPERATOR_ROLE:
                return UserRole.OPERATOR_ROLE_FRIENDLY
            case UserRole.USER_ROLE:
                return UserRole.USER_ROLE_FRIENDLY

    @staticmethod
    def to_formal(role_friendly_name):
        match role_friendly_name:
            case UserRole.ADMIN_ROLE_FRIENDLY:
                return UserRole.ADMIN_ROLE
            case UserRole.OPERATOR_ROLE_FRIENDLY:
                return UserRole.OPERATOR_ROLE
            case UserRole.USER_ROLE_FRIENDLY:
                return UserRole.USER_ROLE
