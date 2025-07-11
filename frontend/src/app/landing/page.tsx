"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Sparkles, 
  TrendingUp, 
  Clock, 
  BarChart3, 
  Zap, 
  Users, 
  ShoppingCart, 
  Star, 
  ArrowRight, 
  CheckCircle, 
  Bot,
  MapPin,
  CreditCard,
  Smartphone,
  Globe,
  Mail,
  Twitter,
  Instagram,
  Linkedin
} from "lucide-react";
import { useState, useEffect } from "react";

export default function LandingPage() {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const features = [
    {
      icon: Bot,
      title: "AI-Powered Recommendations",
      description: "Smart algorithms analyze customer preferences to suggest perfect menu items and increase order value."
    },
    {
      icon: Clock,
      title: "Real-Time Order Tracking",
      description: "Keep customers informed with live updates from kitchen to delivery, reducing support calls."
    },
    {
      icon: BarChart3,
      title: "Advanced Analytics",
      description: "Comprehensive insights into sales patterns, customer behavior, and operational efficiency."
    },
    {
      icon: Users,
      title: "Multi-Restaurant Support",
      description: "Manage multiple locations seamlessly with centralized dashboard and unified reporting."
    },
    {
      icon: TrendingUp,
      title: "Revenue Optimization",
      description: "Increase average order value by 25% through intelligent upselling and cross-selling."
    },
    {
      icon: Zap,
      title: "Lightning Fast",
      description: "Orders processed in under 30 seconds with 99.9% uptime guarantee for peak performance."
    }
  ];

  const testimonials = [
    {
      name: "Sarah Chen",
      role: "Restaurant Owner",
      company: "Golden Dragon",
      content: "Our revenue increased by 40% in just 3 months. The AI recommendations are incredibly accurate!",
      rating: 5
    },
    {
      name: "Marcus Rodriguez",
      role: "Operations Manager",
      company: "Fast Feast Chain",
      content: "Managing 15 locations has never been easier. The analytics help us optimize everything.",
      rating: 5
    },
    {
      name: "Lisa Park",
      role: "Customer Experience Lead",
      company: "Bistro Modern",
      content: "Customer satisfaction scores jumped to 4.8/5. The real-time tracking is a game-changer.",
      rating: 5
    }
  ];

  const pricingPlans = [
    {
      name: "Starter",
      price: "$99",
      description: "Perfect for single restaurant",
      features: ["AI Recommendations", "Basic Analytics", "Order Tracking", "24/7 Support"],
      popular: false
    },
    {
      name: "Professional",
      price: "$199",
      description: "For growing restaurant chains",
      features: ["Everything in Starter", "Advanced Analytics", "Multi-location", "Custom Integrations"],
      popular: true
    },
    {
      name: "Enterprise",
      price: "Custom",
      description: "For large restaurant groups",
      features: ["Everything in Pro", "White-label Solution", "Dedicated Support", "Custom Development"],
      popular: false
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-purple-50">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md border-b border-purple-100 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">Tably</span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-700 hover:text-purple-600 transition-colors">Features</a>
              <a href="#pricing" className="text-gray-700 hover:text-purple-600 transition-colors">Pricing</a>
              <a href="#testimonials" className="text-gray-700 hover:text-purple-600 transition-colors">Reviews</a>
              <Button variant="outline" className="border-purple-300 text-purple-700 hover:bg-purple-50">
                Sign In
              </Button>
              <Button className="bg-purple-600 hover:bg-purple-700">
                Get Started
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        <div 
          className="absolute inset-0 bg-gradient-to-r from-purple-600/10 to-purple-800/10"
          style={{ transform: `translateY(${scrollY * 0.5}px)` }}
        />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <Badge className="mb-4 bg-purple-100 text-purple-800 hover:bg-purple-200">
              <Sparkles className="w-4 h-4 mr-2" />
              AI-Powered Restaurant Technology
            </Badge>
            <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
              Transform Your
              <span className="text-purple-gradient block">Restaurant</span>
              with AI Ordering
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Boost revenue by 40% with intelligent recommendations, streamline operations with real-time tracking, 
              and delight customers with personalized ordering experiences.
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4 mb-12">
              <Button size="lg" className="bg-purple-600 hover:bg-purple-700 text-lg px-8 py-4">
                Start Free Trial
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
              <Button size="lg" variant="outline" className="border-purple-300 text-purple-700 hover:bg-purple-50 text-lg px-8 py-4">
                Watch Demo
              </Button>
            </div>
            <div className="flex justify-center items-center gap-8 text-sm text-gray-500">
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                14-day free trial
              </div>
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                No setup fees
              </div>
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                Cancel anytime
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-4">
              Powerful Features for Modern Restaurants
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Everything you need to streamline operations, increase revenue, and create exceptional customer experiences.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="group hover:shadow-lg transition-all duration-300 border-purple-100 hover:border-purple-300">
                <CardHeader>
                  <div className="w-12 h-12 bg-purple-gradient rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <feature.icon className="w-6 h-6 text-white" />
                  </div>
                  <CardTitle className="text-xl font-semibold">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-600">{feature.description}</CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-gradient-to-b from-purple-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-xl text-gray-600">
              Get started in minutes with our simple 3-step process
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                step: "01",
                title: "Quick Setup",
                description: "Connect your existing POS system or upload your menu. Our AI learns your restaurant in minutes.",
                icon: Smartphone
              },
              {
                step: "02",
                title: "AI Training",
                description: "Our intelligent system analyzes your menu, customer patterns, and optimizes recommendations.",
                icon: Bot
              },
              {
                step: "03",
                title: "Start Growing",
                description: "Launch your AI-powered ordering system and watch your revenue grow with smart recommendations.",
                icon: TrendingUp
              }
            ].map((step, index) => (
              <div key={index} className="text-center group">
                <div className="relative mb-8">
                  <div className="w-20 h-20 bg-purple-gradient rounded-full flex items-center justify-center mx-auto group-hover:scale-110 transition-transform">
                    <step.icon className="w-10 h-10 text-white" />
                  </div>
                  <div className="absolute -top-2 -right-2 w-8 h-8 bg-purple-800 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">{step.step}</span>
                  </div>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">{step.title}</h3>
                <p className="text-gray-600">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-4">
              Trusted by Restaurant Owners
            </h2>
            <p className="text-xl text-gray-600">
              Join thousands of restaurants already growing with Tably
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow border-purple-100">
                <CardHeader>
                  <div className="flex items-center space-x-1 mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                  <CardDescription className="text-gray-700 italic">
                    "{testimonial.content}"
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center">
                    <div className="w-12 h-12 bg-purple-gradient rounded-full flex items-center justify-center mr-4">
                      <span className="text-white font-bold">{testimonial.name.charAt(0)}</span>
                    </div>
                    <div>
                      <CardTitle className="text-lg">{testimonial.name}</CardTitle>
                      <p className="text-sm text-gray-500">{testimonial.role} at {testimonial.company}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 bg-gradient-to-b from-purple-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-gray-600">
              Choose the perfect plan for your restaurant's needs
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {pricingPlans.map((plan, index) => (
              <Card key={index} className={`relative hover:shadow-lg transition-all duration-300 ${
                plan.popular ? 'border-purple-300 shadow-lg scale-105' : 'border-purple-100'
              }`}>
                {plan.popular && (
                  <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-purple-600 text-white">
                    Most Popular
                  </Badge>
                )}
                <CardHeader className="text-center">
                  <CardTitle className="text-2xl font-bold">{plan.name}</CardTitle>
                  <div className="mt-4">
                    <span className="text-4xl font-bold text-purple-600">{plan.price}</span>
                    {plan.price !== "Custom" && <span className="text-gray-500">/month</span>}
                  </div>
                  <CardDescription>{plan.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3 mb-8">
                    {plan.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-center">
                        <CheckCircle className="w-5 h-5 text-green-500 mr-3" />
                        <span className="text-gray-600">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <Button 
                    className={`w-full ${
                      plan.popular 
                        ? 'bg-purple-600 hover:bg-purple-700' 
                        : 'bg-white border-purple-300 text-purple-700 hover:bg-purple-50'
                    }`}
                    variant={plan.popular ? "default" : "outline"}
                  >
                    {plan.price === "Custom" ? "Contact Sales" : "Start Free Trial"}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-purple-gradient">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">
            Ready to Transform Your Restaurant?
          </h2>
          <p className="text-xl text-purple-100 mb-8">
            Join thousands of restaurants already growing their revenue with AI-powered ordering. Start your free trial today!
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4 mb-8">
            <Button size="lg" className="bg-white text-purple-600 hover:bg-gray-50 text-lg px-8 py-4">
              Start Free Trial
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
            <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10 text-lg px-8 py-4">
              Schedule Demo
            </Button>
          </div>
          <div className="flex justify-center items-center gap-8 text-sm text-purple-200">
            <div className="flex items-center">
              <CreditCard className="w-5 h-5 mr-2" />
              No credit card required
            </div>
            <div className="flex items-center">
              <Clock className="w-5 h-5 mr-2" />
              Setup in 5 minutes
            </div>
            <div className="flex items-center">
              <Users className="w-5 h-5 mr-2" />
              24/7 support included
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center">
                  <Bot className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold">Tably</span>
              </div>
              <p className="text-gray-400 mb-6 max-w-md">
                Revolutionizing restaurant ordering with AI-powered recommendations, real-time tracking, and advanced analytics.
              </p>
              <div className="flex space-x-4">
                <Button size="icon" variant="ghost" className="text-gray-400 hover:text-white">
                  <Twitter className="w-5 h-5" />
                </Button>
                <Button size="icon" variant="ghost" className="text-gray-400 hover:text-white">
                  <Instagram className="w-5 h-5" />
                </Button>
                <Button size="icon" variant="ghost" className="text-gray-400 hover:text-white">
                  <Linkedin className="w-5 h-5" />
                </Button>
              </div>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Product</h3>
              <ul className="space-y-2">
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Features</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">API</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Integrations</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Support</h3>
              <ul className="space-y-2">
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Help Center</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Contact</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Status</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Security</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 mt-8 flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-400 text-sm">
              © 2024 Tably. All rights reserved.
            </p>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">Privacy Policy</a>
              <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">Terms of Service</a>
              <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">Cookie Policy</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}