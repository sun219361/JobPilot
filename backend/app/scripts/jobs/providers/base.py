"""채용공고 Provider 인터페이스"""

from abc import ABC, abstractmethod

from app.scripts.jobs.job_posting_item import JobPostingItem


class BaseJobProvider(ABC):
    """모든 채용공고 provider가 구현해야 하는 인터페이스.

    구현체는 company_name 기준으로 채용공고를 검색하고
    JobPostingItem 리스트를 반환한다.

    설계 원칙:
    - API 키 미설정 / 요청 실패 시 예외를 raise하지 않고 빈 리스트 반환.
      → graceful failure. 배치 스크립트가 계속 다음 기업을 처리할 수 있다.
    - dry-run 제어는 collect_jobs.py 레벨에서 담당.
      provider는 항상 같은 결과를 반환하며 저장 여부를 모른다.
    """

    @abstractmethod
    def fetch(
        self,
        company_name: str,
        limit: int = 5,
    ) -> list[JobPostingItem]:
        """기업명으로 채용공고를 검색해 JobPostingItem 리스트 반환.

        Args:
            company_name: 검색할 기업명
            limit:        최대 반환 개수

        Returns:
            JobPostingItem 리스트. 실패 시 빈 리스트.
        """

    @property
    @abstractmethod
    def source_name(self) -> str:
        """provider 식별자 문자열 (DB source_name 컬럼에 저장).
        예: "saramin", "wanted", "jobkorea"
        """
