import { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, Clock, XCircle } from 'lucide-react';
import { NodeStatus } from '@/types/roadmap';
import { cn } from '@/lib/utils';

interface CourseNodeProps {
  data: {
    id: string;
    code: string;
    title: string;
    type: 'core' | 'elective';
    status: NodeStatus;
    onClick: (nodeId: string) => void;
  };
  selected?: boolean;
}

const statusIcons = {
  'not-started': null,
  'in-progress': Clock,
  'completed': CheckCircle,
  'skipped': XCircle,
};

const statusColors = {
  'not-started': 'bg-background border-border',
  'in-progress': 'bg-warning/10 border-warning',
  'completed': 'bg-success/10 border-success',
  'skipped': 'bg-muted border-muted-foreground',
};

export const CourseNode = memo(({ data, selected }: CourseNodeProps) => {
  const StatusIcon = statusIcons[data.status];
  
  return (
    <div className="course-node">
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-border border-2 border-background"
      />
      
      <div
        className={cn(
          "min-w-[200px] max-w-[250px] p-3 rounded-lg border-2 transition-all duration-200 cursor-pointer bg-card",
          statusColors[data.status],
          selected && "ring-2 ring-ring ring-offset-2",
          "hover:shadow-md hover:scale-105"
        )}
        onClick={() => data.onClick(data.id)}
      >
        <div className="flex items-start gap-2">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <Badge 
                variant={data.type === 'core' ? 'default' : 'secondary'}
                className="text-xs"
              >
                {data.type === 'core' ? 'Core' : 'Elective'}
              </Badge>
              {StatusIcon && (
                <StatusIcon 
                  className={cn(
                    "w-4 h-4",
                    data.status === 'completed' && "text-success",
                    data.status === 'in-progress' && "text-warning",
                    data.status === 'skipped' && "text-muted-foreground"
                  )}
                />
              )}
            </div>
            
            <div className="text-xs text-muted-foreground font-mono mb-1">
              {data.code}
            </div>
            
            <div className="text-sm font-medium leading-tight text-foreground">
              {data.title}
            </div>
          </div>
        </div>
      </div>
      
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 !bg-border border-2 border-background"
      />
    </div>
  );
});

CourseNode.displayName = 'CourseNode';