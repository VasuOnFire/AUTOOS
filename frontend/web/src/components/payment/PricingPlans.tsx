"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  Check,
  Zap,
  Users,
  Briefcase,
  Building,
  Sparkles,
  Crown,
} from "lucide-react";
import toast from "react-hot-toast";

interface PricingPlan {
  id: string;
  name: string;
  price: number;
  annualPrice: number;
  description: string;
  icon: React.ReactNode;
  features: string[];
  workflows: string;
  agents: string;
  popular?: boolean;
  isTrial?: boolean;
}

interface PricingPlansProps {
  currentPlan?: string;
  onSelectPlan?: (planId: string, isAnnual: boolean) => void;
  onStartTrial?: () => void;
}

export default function PricingPlans({
  currentPlan,
  onSelectPlan,
  onStartTrial,
}: PricingPlansProps) {
  const [billingCycle, setBillingCycle] = useState<"monthly" | "annual">("monthly");
  const [loading, setLoading] = useState<string | null>(null);

  const plans: PricingPlan[] = [
    {
      id: "trial",
      name: "Free Trial",
      price: 0,
      annualPrice: 0,
      description: "30 Days Free - No Credit Card Required",
      icon: <Sparkles className="w-6 h-6" />,
      workflows: "10 workflows/month",
      agents: "2 concurrent agents",
      isTrial: true,
      features: [
        "30-day free trial",
        "No credit card required",
        "10 workflows per month",
        "2 concurrent agents",
        "Basic support",
        "Access to all core features",
      ],
    },
    {
      id: "student",
      name: "Student",
      price: 9.99,
      annualPrice: 99.99,
      description: "Perfect for students and learners",
      icon: <Zap className="w-6 h-6" />,
      workflows: "100 workflows/month",
      agents: "5 concurrent agents",
      features: [
        "100 workflows per month",
        "5 concurrent agents",
        "Email support",
        "Student verification required",
        "All core features",
        "Community access",
      ],
    },
    {
      id: "employee",
      name: "Employee",
      price: 29.99,
      annualPrice: 299.99,
      description: "For professionals and teams",
      icon: <Users className="w-6 h-6" />,
      workflows: "500 workflows/month",
      agents: "20 concurrent agents",
      popular: true,
      features: [
        "500 workflows per month",
        "20 concurrent agents",
        "Priority email support",
        "Advanced analytics",
        "Team collaboration",
        "API access",
      ],
    },
    {
      id: "professional",
      name: "Professional",
      price: 99.99,
      annualPrice: 999.99,
      description: "For power users and businesses",
      icon: <Briefcase className="w-6 h-6" />,
      workflows: "Unlimited workflows",
      agents: "100 concurrent agents",
      features: [
        "Unlimited workflows",
        "100 concurrent agents",
        "24/7 priority support",
        "Advanced analytics & reporting",
        "Custom integrations",
        "Dedicated account manager",
        "SLA guarantee",
      ],
    },
    {
      id: "enterprise",
      name: "Enterprise",
      price: 0,
      annualPrice: 0,
      description: "Custom pricing for large organizations",
      icon: <Building className="w-6 h-6" />,
      workflows: "Unlimited workflows",
      agents: "Unlimited agents",
      features: [
        "Unlimited everything",
        "Dedicated infrastructure",
        "24/7 premium support",
        "Custom SLA",
        "On-premise deployment option",
        "Advanced security features",
        "Custom training & onboarding",
        "Dedicated success team",
      ],
    },
  ];

  const handleSelectPlan = async (planId: string) => {
    if (planId === "trial") {
      if (onStartTrial) {
        setLoading(planId);
        try {
          await onStartTrial();
          toast.success("Free trial activated!");
        } catch (error: any) {
          toast.error(error.message || "Failed to start trial");
        } finally {
          setLoading(null);
        }
      }
      return;
    }

    if (planId === "enterprise") {
      window.location.href = "mailto:sales@autoos.ai?subject=Enterprise Plan Inquiry";
      return;
    }

    if (onSelectPlan) {
      setLoading(planId);
      try {
        await onSelectPlan(planId, billingCycle === "annual");
        toast.success("Redirecting to checkout...");
      } catch (error: any) {
        toast.error(error.message || "Failed to select plan");
      } finally {
        setLoading(null);
      }
    }
  };

  const getPrice = (plan: PricingPlan) => {
    if (plan.price === 0) return "Free";
    if (plan.id === "enterprise") return "Custom";
    const price = billingCycle === "annual" ? plan.annualPrice : plan.price;
    return `$${price.toFixed(2)}`;
  };

  const getSavings = (plan: PricingPlan) => {
    if (plan.price === 0 || plan.id === "enterprise") return null;
    const monthlyCost = plan.price * 12;
    const savings = monthlyCost - plan.annualPrice;
    const percentage = Math.round((savings / monthlyCost) * 100);
    return { amount: savings, percentage };
  };

  return (
    <div className="w-full max-w-7xl mx-auto px-4 py-12">
      {/* Header */}
      <div className="text-center mb-12">
        <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          Choose Your Plan
        </h2>
        <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">
          Start with a 30-day free trial. No credit card required.
        </p>

        {/* Billing Toggle */}
        <div className="inline-flex items-center gap-4 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
          <button
            onClick={() => setBillingCycle("monthly")}
            className={`px-6 py-2 rounded-lg font-medium transition-all ${
              billingCycle === "monthly"
                ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm"
                : "text-gray-600 dark:text-gray-400"
            }`}
          >
            Monthly
          </button>
          <button
            onClick={() => setBillingCycle("annual")}
            className={`px-6 py-2 rounded-lg font-medium transition-all ${
              billingCycle === "annual"
                ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm"
                : "text-gray-600 dark:text-gray-400"
            }`}
          >
            Annual
            <span className="ml-2 px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 text-xs rounded-full">
              Save up to 17%
            </span>
          </button>
        </div>
      </div>

      {/* Pricing Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
        {plans.map((plan, index) => {
          const savings = getSavings(plan);
          const isCurrentPlan = currentPlan === plan.id;

          return (
            <motion.div
              key={plan.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className={`relative bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden ${
                plan.popular ? "ring-2 ring-blue-600" : ""
              } ${plan.isTrial ? "ring-2 ring-green-600" : ""}`}
            >
              {/* Popular Badge */}
              {plan.popular && (
                <div className="absolute top-0 right-0 bg-blue-600 text-white px-4 py-1 text-sm font-semibold rounded-bl-lg">
                  Most Popular
                </div>
              )}

              {/* Trial Badge */}
              {plan.isTrial && (
                <div className="absolute top-0 right-0 bg-green-600 text-white px-4 py-1 text-sm font-semibold rounded-bl-lg flex items-center gap-1">
                  <Sparkles className="w-4 h-4" />
                  FREE
                </div>
              )}

              {/* Current Plan Badge */}
              {isCurrentPlan && (
                <div className="absolute top-0 left-0 bg-purple-600 text-white px-4 py-1 text-sm font-semibold rounded-br-lg flex items-center gap-1">
                  <Crown className="w-4 h-4" />
                  Current
                </div>
              )}

              <div className="p-6">
                {/* Icon */}
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center mb-4 ${
                  plan.isTrial
                    ? "bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400"
                    : plan.popular
                    ? "bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400"
                    : "bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400"
                }`}>
                  {plan.icon}
                </div>

                {/* Plan Name */}
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  {plan.name}
                </h3>

                {/* Description */}
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  {plan.description}
                </p>

                {/* Price */}
                <div className="mb-6">
                  <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-bold text-gray-900 dark:text-white">
                      {getPrice(plan)}
                    </span>
                    {plan.price > 0 && plan.id !== "enterprise" && (
                      <span className="text-gray-600 dark:text-gray-400">
                        /{billingCycle === "annual" ? "year" : "month"}
                      </span>
                    )}
                  </div>
                  {billingCycle === "annual" && savings && (
                    <p className="text-sm text-green-600 dark:text-green-400 mt-1">
                      Save ${savings.amount.toFixed(2)} ({savings.percentage}%)
                    </p>
                  )}
                </div>

                {/* Usage Limits */}
                <div className="mb-6 space-y-2">
                  <div className="flex items-center gap-2 text-sm">
                    <div className="w-2 h-2 bg-blue-600 rounded-full" />
                    <span className="text-gray-700 dark:text-gray-300">{plan.workflows}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <div className="w-2 h-2 bg-purple-600 rounded-full" />
                    <span className="text-gray-700 dark:text-gray-300">{plan.agents}</span>
                  </div>
                </div>

                {/* Features */}
                <ul className="space-y-3 mb-6">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <Check className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
                      <span className="text-sm text-gray-700 dark:text-gray-300">
                        {feature}
                      </span>
                    </li>
                  ))}
                </ul>

                {/* CTA Button */}
                <button
                  onClick={() => handleSelectPlan(plan.id)}
                  disabled={loading === plan.id || isCurrentPlan}
                  className={`w-full py-3 rounded-lg font-semibold transition-all duration-200 ${
                    isCurrentPlan
                      ? "bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed"
                      : plan.isTrial
                      ? "bg-gradient-to-r from-green-600 to-emerald-600 text-white hover:from-green-700 hover:to-emerald-700"
                      : plan.popular
                      ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700"
                      : "bg-gray-900 dark:bg-white text-white dark:text-gray-900 hover:bg-gray-800 dark:hover:bg-gray-100"
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  {loading === plan.id ? (
                    <div className="flex items-center justify-center gap-2">
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Loading...
                    </div>
                  ) : isCurrentPlan ? (
                    "Current Plan"
                  ) : plan.isTrial ? (
                    "Start Free Trial"
                  ) : plan.id === "enterprise" ? (
                    "Contact Sales"
                  ) : (
                    "Get Started"
                  )}
                </button>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Comparison Table Link */}
      <div className="text-center mt-12">
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          Need help choosing? Compare all features side-by-side
        </p>
        <button className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-semibold">
          View Detailed Comparison →
        </button>
      </div>
    </div>
  );
}
