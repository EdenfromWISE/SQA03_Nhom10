import React from "react";
import styles from "./LandingPage.module.css";
import HeroSection from '../components/HeroSection';
import FeatureSection from '../components/FeatureSection';
import LearningMethodSection from "../components/LearningMethodSection";
import Footer from '../components/Footer';
import FeedbackSection from '../components/FeedbackSection';
import { useDocumentTitle } from '../hooks/useDocumentTitle';

const LandingPage = () => {
  useDocumentTitle('Trang chủ');
  return (
    <div className={styles.container}>
    <HeroSection />
    <FeatureSection />
    <LearningMethodSection />
    <FeedbackSection />
    <Footer />
    </div>
  );
};

export default LandingPage;
