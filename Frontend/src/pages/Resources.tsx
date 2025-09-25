import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ExternalLink, Home, BookOpen, Award, LifeBuoy, Users, Code, Calendar } from 'lucide-react';

const resourceCategories = [
  {
    title: "Official WWU CS Resources",
    icon: BookOpen,
    resources: [
      {
        title: "CS Department Homepage",
        description: "Main department page with news, faculty info, and general information",
        url: "https://cs.wwu.edu/",
        icon: Home
      },
      {
        title: "Resources & Information",
        description: "Student resources, academic policies, and departmental information",
        url: "https://cs.wwu.edu/resources-and-information",
        icon: BookOpen
      },
      {
        title: "Scholarship Awards",
        description: "Information about departmental scholarships and financial aid",
        url: "https://cs.wwu.edu/computer-science-departmental-scholarship-awards",
        icon: Award
      },
      {
        title: "Student Survival Guide",
        description: "Comprehensive guide for CS students with tips and resources",
        url: "https://support.cs.wwu.edu/home/survival_guide/index.html",
        icon: LifeBuoy
      }
    ]
  },
  {
    title: "Academic Support",
    icon: Users,
    resources: [
      {
        title: "Academic Advising",
        description: "Schedule meetings with academic advisors for course planning",
        url: "https://cs.wwu.edu/advising",
        icon: Users
      },
      {
        title: "Course Catalog",
        description: "Browse available CS courses and their descriptions",
        url: "https://catalog.wwu.edu/preview_program.php?catoid=22&poid=14473",
        icon: BookOpen
      },
      {
        title: "Registration Information",
        description: "Important dates and registration procedures",
        url: "https://registrar.wwu.edu/",
        icon: Calendar
      }
    ]
  },
  {
    title: "Programming & Technical",
    icon: Code,
    resources: [
      {
        title: "CS Lab Information",
        description: "Computer lab locations, hours, and technical support",
        url: "https://support.cs.wwu.edu/",
        icon: Code
      },
      {
        title: "Student Email & Computing",
        description: "IT services and email setup for students",
        url: "https://support.wwu.edu/",
        icon: Code
      }
    ]
  }
];

export const Resources = () => {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-wwu-primary">WWU CS Resources</h1>
              <p className="text-muted-foreground mt-1">
                Curated resources for Western Washington University Computer Science students
              </p>
            </div>
            <Link to="/">
              <Button variant="outline">
                <Home className="w-4 h-4 mr-2" />
                Back to Home
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="py-12">
        <div className="container mx-auto px-4">
          {/* Intro Section */}
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Everything You Need to Succeed</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Access official WWU CS resources, academic support, and technical tools 
              to help you navigate your computer science education successfully.
            </p>
          </div>

          {/* Resource Categories */}
          <div className="space-y-12">
            {resourceCategories.map((category) => {
              const CategoryIcon = category.icon;
              
              return (
                <section key={category.title}>
                  <div className="flex items-center gap-3 mb-6">
                    <div className="w-10 h-10 bg-wwu-primary/10 rounded-lg flex items-center justify-center">
                      <CategoryIcon className="w-5 h-5 text-wwu-primary" />
                    </div>
                    <h3 className="text-2xl font-bold">{category.title}</h3>
                  </div>
                  
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {category.resources.map((resource) => {
                      const ResourceIcon = resource.icon;
                      
                      return (
                        <Card key={resource.title} className="h-full hover:shadow-lg transition-all duration-200 hover:scale-105">
                          <CardHeader>
                            <div className="flex items-start gap-3">
                              <div className="w-8 h-8 bg-surface rounded-lg flex items-center justify-center flex-shrink-0 mt-1">
                                <ResourceIcon className="w-4 h-4 text-wwu-primary" />
                              </div>
                              <div className="min-w-0">
                                <CardTitle className="text-lg leading-tight">{resource.title}</CardTitle>
                                <CardDescription className="text-sm mt-1">
                                  {resource.description}
                                </CardDescription>
                              </div>
                            </div>
                          </CardHeader>
                          
                          <CardContent>
                            <Button 
                              asChild 
                              className="w-full bg-wwu-primary hover:bg-wwu-primary/90"
                            >
                              <a 
                                href={resource.url} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="flex items-center justify-center"
                              >
                                Visit Resource
                                <ExternalLink className="w-4 h-4 ml-2" />
                              </a>
                            </Button>
                          </CardContent>
                        </Card>
                      );
                    })}
                  </div>
                </section>
              );
            })}
          </div>

          {/* Additional Help Section */}
          <section className="mt-16 p-8 bg-surface rounded-2xl">
            <div className="text-center">
              <h3 className="text-2xl font-bold mb-4">Need More Help?</h3>
              <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
                If you can't find what you're looking for, don't hesitate to reach out to 
                the CS department directly or visit the student support services.
              </p>
              
              <div className="flex flex-wrap justify-center gap-4">
                <Button variant="outline" asChild>
                  <a href="mailto:csadvise@wwu.edu" className="flex items-center">
                    <Users className="w-4 h-4 mr-2" />
                    Contact Advising
                  </a>
                </Button>
                
                <Button variant="outline" asChild>
                  <a 
                    href="https://cs.wwu.edu/contact" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="flex items-center"
                  >
                    <ExternalLink className="w-4 h-4 mr-2" />
                    Department Contact
                  </a>
                </Button>
              </div>
            </div>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-8 border-t border-border">
        <div className="container mx-auto px-4 text-center">
          <p className="text-sm text-muted-foreground">
            Resources compiled for WWU CS students. Always check official WWU websites for the most current information.
          </p>
        </div>
      </footer>
    </div>
  );
};