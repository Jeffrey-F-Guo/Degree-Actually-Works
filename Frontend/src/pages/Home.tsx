import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ArrowRight, BookOpen, Users, Target } from 'lucide-react';

// Import the paths data
import pathsData from '@/data/paths.json';
import { RoadmapPath } from '@/types/roadmap';

export const Home = () => {
  const paths = pathsData.paths as RoadmapPath[];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-wwu-primary">WWU CS Roadmaps</h1>
              <p className="text-muted-foreground mt-1">
                Interactive course roadmaps for Western Washington University Computer Science students
              </p>
            </div>
            <Link to="/resources">
              <Button variant="outline">
                <BookOpen className="w-4 h-4 mr-2" />
                Resources
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-16 bg-gradient-to-b from-surface to-background">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-6">
            Plan Your CS Journey
          </h2>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Navigate your computer science education with interactive dependency graphs, 
            progress tracking, and curated course recommendations tailored to your career goals.
          </p>
          
          <div className="flex flex-wrap justify-center gap-4 mb-12">
            <div className="flex items-center gap-2 bg-card px-4 py-2 rounded-full border">
              <Target className="w-4 h-4 text-wwu-primary" />
              <span className="text-sm">Goal-Oriented Paths</span>
            </div>
            <div className="flex items-center gap-2 bg-card px-4 py-2 rounded-full border">
              <Users className="w-4 h-4 text-wwu-primary" />
              <span className="text-sm">Peer Collaboration</span>
            </div>
            <div className="flex items-center gap-2 bg-card px-4 py-2 rounded-full border">
              <BookOpen className="w-4 h-4 text-wwu-primary" />
              <span className="text-sm">Progress Tracking</span>
            </div>
          </div>
        </div>
      </section>

      {/* Paths Section */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold mb-4">Choose Your Path</h3>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Select a specialization track that aligns with your career goals. 
              Each path includes core requirements and recommended electives with clear prerequisites.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {paths.map((path) => (
              <Card key={path.slug} className="h-full hover:shadow-lg transition-all duration-200 hover:scale-105">
                <CardHeader>
                  <div className="flex items-start justify-between mb-2">
                    <CardTitle className="text-xl">{path.name}</CardTitle>
                    <Badge variant="outline" className="text-xs">
                      {path.groups.reduce((acc, group) => acc + group.nodes.length, 0)} courses
                    </Badge>
                  </div>
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
                      {path.coreEmphasis.slice(0, 3).map((emphasis, index) => (
                        <div key={index} className="text-xs text-muted-foreground flex items-center">
                          <div className="w-1.5 h-1.5 bg-wwu-primary rounded-full mr-2" />
                          {emphasis}
                        </div>
                      ))}
                      {path.coreEmphasis.length > 3 && (
                        <div className="text-xs text-muted-foreground">
                          +{path.coreEmphasis.length - 3} more areas
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="pt-4">
                    <Link to={`/path/${path.slug}`}>
                      <Button className="w-full bg-wwu-primary hover:bg-wwu-primary/90">
                        Start {path.name}
                        <ArrowRight className="w-4 h-4 ml-2" />
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-surface">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold mb-4">Why Use Roadmaps?</h3>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Make informed decisions about your course selection with visual dependency graphs 
              and progress tracking.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 bg-wwu-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Target className="w-6 h-6 text-wwu-primary" />
              </div>
              <h4 className="font-semibold mb-2">Clear Prerequisites</h4>
              <p className="text-sm text-muted-foreground">
                Visualize course dependencies and plan your semester schedule effectively.
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-wwu-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                <BookOpen className="w-6 h-6 text-wwu-primary" />
              </div>
              <h4 className="font-semibold mb-2">Progress Tracking</h4>
              <p className="text-sm text-muted-foreground">
                Track your completed courses and see your progress toward graduation.
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-wwu-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Users className="w-6 h-6 text-wwu-primary" />
              </div>
              <h4 className="font-semibold mb-2">Share & Collaborate</h4>
              <p className="text-sm text-muted-foreground">
                Share your progress with advisors and collaborate with peers.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-border">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h4 className="font-bold text-lg mb-4 text-wwu-primary">WWU CS Roadmaps</h4>
              <p className="text-sm text-muted-foreground mb-4">
                An interactive tool to help Western Washington University Computer Science 
                students plan their academic journey and career preparation.
              </p>
              <div className="flex gap-4">
                <Link to="/resources">
                  <Button variant="outline" size="sm">Resources</Button>
                </Link>
              </div>
            </div>
            
            <div>
              <h5 className="font-semibold mb-4">Quick Links</h5>
              <div className="space-y-2">
                <a 
                  href="https://cs.wwu.edu/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="block text-sm text-muted-foreground hover:text-wwu-primary transition-colors"
                >
                  WWU CS Department
                </a>
                <a 
                  href="https://cs.wwu.edu/resources-and-information" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="block text-sm text-muted-foreground hover:text-wwu-primary transition-colors"
                >
                  Student Resources
                </a>
                <a 
                  href="https://support.cs.wwu.edu/home/survival_guide/index.html" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="block text-sm text-muted-foreground hover:text-wwu-primary transition-colors"
                >
                  Survival Guide
                </a>
              </div>
            </div>
          </div>
          
          <div className="mt-8 pt-8 border-t border-border text-center">
            <p className="text-sm text-muted-foreground">
              Made with ❤️ for WWU CS students. Not officially affiliated with Western Washington University.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};