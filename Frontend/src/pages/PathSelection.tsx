import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowRight } from 'lucide-react';

// Import the paths data
import pathsData from '@/data/paths.json';
import { RoadmapPath } from '@/types/roadmap';

export const PathSelection = () => {
  const navigate = useNavigate();
  const paths = pathsData.paths as RoadmapPath[];

  const handlePathSelect = (path: RoadmapPath) => {
    navigate(`/roadmap/${path.slug}`);
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Choose Your Path</h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Select a specialization track to view the interactive course roadmap.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {paths.map((path) => (
            <Card 
              key={path.slug} 
              className="h-full hover:shadow-lg transition-all duration-200 hover:scale-105 cursor-pointer"
              onClick={() => handlePathSelect(path)}
            >
              <CardHeader>
                <CardTitle className="text-xl">{path.name}</CardTitle>
                <CardDescription className="text-sm">
                  {path.goal}
                </CardDescription>
              </CardHeader>
              
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  {path.summary}
                </p>
                
                <div className="space-y-2">
                  <div className="text-sm font-medium">Core Focus:</div>
                  <div className="space-y-1">
                    {path.coreEmphasis.slice(0, 2).map((emphasis, index) => (
                      <div key={index} className="text-xs text-muted-foreground flex items-center">
                        <div className="w-1.5 h-1.5 bg-primary rounded-full mr-2" />
                        {emphasis}
                      </div>
                    ))}
                    {path.coreEmphasis.length > 2 && (
                      <div className="text-xs text-muted-foreground">
                        +{path.coreEmphasis.length - 2} more areas
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="pt-4">
                  <Button className="w-full">
                    View Roadmap
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};
