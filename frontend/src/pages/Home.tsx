
import { useNavigate } from "react-router-dom";
import { ArrowRightCircle, MessageSquareText, CheckCircle, Zap, Users } from "lucide-react";
import { Button } from "@/components/ui/button";

const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-50">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 flex flex-col lg:flex-row items-center gap-12">
        <div className="flex-1 space-y-6">
          <div className="inline-block px-3 py-1 rounded-full bg-blue-100 text-blue-700 text-sm font-medium">
            Enterprise AI Assistant
          </div>
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900">
            Streamline your business processes using <span className="text-purple-600">Rasa</span> with <span className="text-blue-600">BizFlow AI</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl">
            Automate workflows, get instant answers to your questions, and boost productivity across your organization.
          </p>
          <div className="flex flex-wrap gap-4 pt-4">
            <Button
              onClick={() => navigate("/chat")}
              size="lg"
              className="rounded-full shadow-lg"
            >
              Start Conversation <ArrowRightCircle className="ml-2" />
            </Button>
            <Button
              variant="outline"
              size="lg"
              className="rounded-full"
              onClick={() => window.open("https://rasa.com/docs", "_blank")}
            >
              View Documentation
            </Button>
          </div>
        </div>
        <div className="flex-1 flex justify-center">
          <div className="w-full max-w-md bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
            <div className="bg-blue-600 px-6 py-4">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-red-400"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
                <div className="w-3 h-3 rounded-full bg-green-400"></div>
                <div className="ml-2 text-white font-medium">BizFlow AI Chat</div>
              </div>
            </div>
            <div className="p-6 space-y-4">
              <div className="bg-gray-100 rounded-lg p-3 max-w-[80%] text-gray-700">
                Hi there! I'm BizFlow AI. How can I help you today?
              </div>
              <div className="bg-blue-600 rounded-lg p-3 max-w-[80%] ml-auto text-white">
                I need to book a meeting room for tomorrow.
              </div>
              <div className="bg-gray-100 rounded-lg p-3 max-w-[80%] text-gray-700">
                I'd be happy to help you book a meeting room. Could you please provide the time and number of attendees?
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-white py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900">
              Designed for Enterprise Productivity
            </h2>
            <p className="mt-4 text-xl text-gray-600 max-w-3xl mx-auto">
              BizFlow AI handles both structured workflows and open-ended queries to support all your business needs.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-gradient-to-br from-blue-50 to-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-6">
                <MessageSquareText className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">IT Support</h3>
              <p className="text-gray-600">
                Easily raise IT support tickets, check status, and get immediate help for common issues.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-gradient-to-br from-blue-50 to-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-6">
                <CheckCircle className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Process Automation</h3>
              <p className="text-gray-600">
                Submit expense reports, request approvals, and manage workflows through simple conversations.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-gradient-to-br from-blue-50 to-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-6">
                <Zap className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Instant Knowledge</h3>
              <p className="text-gray-600">
                Access the latest HR policies, company information, and documentation without searching through systems.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="container mx-auto px-4 py-20">
        <div className="bg-blue-600 rounded-2xl p-8 md:p-12 shadow-xl">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
              Ready to transform your business processes?
            </h2>
            <p className="text-xl text-blue-100 mb-8">
              Start using BizFlow AI today and see the difference in your team's productivity.
            </p>
            <Button
              onClick={() => navigate("/chat")}
              size="lg"
              variant="secondary"
              className="rounded-full shadow-lg"
            >
              Get Started Now <ArrowRightCircle className="ml-2" />
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-50 border-t border-gray-200 py-12">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center">
                <span className="text-white font-bold text-lg">B</span>
              </div>
              <span className="text-xl font-bold text-gray-800">BizFlow AI</span>
            </div>
            <div className="text-gray-500 text-sm">
              © {new Date().getFullYear()} BizFlow AI. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Home;
