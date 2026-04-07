interface BulletPointListProps {
  items: string[];
  emptyText?: string;
}

export function BulletPointList({
  items,
  emptyText = "준비 중입니다.",
}: BulletPointListProps) {
  if (items.length === 0) {
    return <p className="text-sm text-gray-400">{emptyText}</p>;
  }

  return (
    <ul className="space-y-2">
      {items.map((item, idx) => (
        <li key={idx} className="flex items-start gap-2">
          <span className="mt-1.5 flex-shrink-0 w-1.5 h-1.5 rounded-full bg-blue-400" />
          <span className="text-sm text-gray-700 leading-relaxed">{item}</span>
        </li>
      ))}
    </ul>
  );
}
