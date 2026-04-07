interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export function ErrorState({
  message = "데이터를 불러오는 중 문제가 발생했습니다.",
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <div className="text-4xl mb-3">⚠️</div>
      <p className="text-base font-medium text-gray-700">오류가 발생했습니다</p>
      <p className="mt-1 text-sm text-gray-400 max-w-xs">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 px-4 py-2 rounded-md bg-gray-900 text-white text-sm font-medium hover:bg-gray-700 transition-colors"
        >
          다시 시도
        </button>
      )}
    </div>
  );
}
