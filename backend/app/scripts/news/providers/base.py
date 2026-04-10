"""뉴스 Provider 인터페이스"""

from abc import ABC, abstractmethod

from app.scripts.news.news_item import NewsItem


class BaseNewsProvider(ABC):
    """모든 뉴스 provider가 구현해야 하는 인터페이스.

    구현체는 company_name 기준으로 뉴스를 검색하고
    NewsItem 리스트를 반환한다.
    """

    @abstractmethod
    def fetch(
        self,
        company_name: str,
        limit: int = 5,
    ) -> list[NewsItem]:
        """기업명으로 뉴스를 검색해 NewsItem 리스트 반환.

        API 키 미설정 등 graceful failure 상황에선
        예외를 raise하지 않고 빈 리스트를 반환한다.
        """

    @property
    @abstractmethod
    def source_name(self) -> str:
        """provider 식별자 문자열 (DB source_name 컬럼에 저장)"""
