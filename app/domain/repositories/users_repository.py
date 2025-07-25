from sqlmodel import Session, select

from app.domain.models.users import User


class UsersRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_user_by_email(self, email: str) -> User:
        return self.session.exec((select(User).where(User.email == email), 
                                  User.is_active == True)).first()