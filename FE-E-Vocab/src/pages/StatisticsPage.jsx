import React, { useEffect, useState } from "react";
import styles from "./StatisticsPage.module.css";
import ProgressChart from "../components/Statistics/ProgressChart";
import Achievements from "../components/Statistics/Achievements";
import RecentVocabulary from "../components/Statistics/RecentVocabulary";
import { BookOpen, Plus, RotateCcw, CheckCircle } from "lucide-react";
import CourseProgressChart from "../components/Statistics/CourseProgressChart";
import StreakCalendar from "../components/Statistics/StreakCalendar";
import UpcomingReview from "../components/Statistics/UpcomingReview";
import { getStreakCalendar, getUpcomingReview, getOverview, getDailyProgress, getRecentSessions } from "../services/progressService";
import { useDocumentTitle } from '../hooks/useDocumentTitle';

const StatisticsPage = () => {
  useDocumentTitle('Thống kê');
  const today = new Date();
  const [streakMonth, setStreakMonth] = useState({
    year: today.getFullYear(),
    month: today.getMonth() + 1,
  });
  const [streakData, setStreakData] = useState(null);
  const [streakLoading, setStreakLoading] = useState(false);
  const [streakError, setStreakError] = useState("");
  const [upcomingReviewData, setUpcomingReviewData] = useState([]);
  const [upcomingReviewLoading, setUpcomingReviewLoading] = useState(false);
  const [upcomingReviewError, setUpcomingReviewError] = useState("");
  const [overview, setOverview] = useState({
    totalLearnedCount: 0,
    newWordsToday: 0,
    overdueAndDueTodayNotReviewed: 0,
    dueTodayAndReviewed: 0,
  });
  const [overviewLoading, setOverviewLoading] = useState(false);
  const [dailyProgress, setDailyProgress] = useState([]);
  const [dailyProgressLoading, setDailyProgressLoading] = useState(false);
  const [recentSessions, setRecentSessions] = useState([]);
  const [recentSessionsLoading, setRecentSessionsLoading] = useState(false);

  useEffect(() => {
    let isMounted = true;

    const fetchStreak = async () => {
      setStreakLoading(true);
      setStreakError("");
      try {
        const data = await getStreakCalendar(streakMonth);
        if (isMounted) {
          setStreakData(data);
        }
      } catch {
        if (isMounted) {
          setStreakError("Không thể tải dữ liệu streak. Vui lòng thử lại.");
        }
      } finally {
        if (isMounted) {
          setStreakLoading(false);
        }
      }
    };

    const fetchUpcomingReview = async () => {
      setUpcomingReviewLoading(true);
      setUpcomingReviewError("");
      try {
        const data = await getUpcomingReview(7);
        if (isMounted) {
          setUpcomingReviewData(data);
        }
      } catch (error) {
        if (isMounted) {
          setUpcomingReviewError("Không thể tải dữ liệu từ vựng sắp ôn tập. Vui lòng thử lại.");
          console.error("Error fetching upcoming review:", error);
        }
      } finally {
        if (isMounted) {
          setUpcomingReviewLoading(false);
        }
      }
    };

    const fetchOverview = async () => {
      setOverviewLoading(true);
      try {
        const data = await getOverview();
        if (isMounted) {
          setOverview({
            totalLearnedCount: data.total_learned_count || 0,
            newWordsToday: data.new_words_today || 0,
            overdueAndDueTodayNotReviewed: data.overdue_and_due_today_not_reviewed || 0,
            dueTodayAndReviewed: data.due_today_and_reviewed || 0,
          });
        }
      } catch (error) {
        if (isMounted) {
          console.error("Error fetching overview:", error);
        }
      } finally {
        if (isMounted) {
          setOverviewLoading(false);
        }
      }
    };

    const fetchDailyProgress = async () => {
      setDailyProgressLoading(true);
      try {
        const data = await getDailyProgress();
        if (isMounted) {
          setDailyProgress(data || []);
        }
      } catch (error) {
        if (isMounted) {
          console.error("Error fetching daily progress:", error);
          setDailyProgress([]);
        }
      } finally {
        if (isMounted) {
          setDailyProgressLoading(false);
        }
      }
    };

    const fetchRecentSessions = async () => {
      setRecentSessionsLoading(true);
      try {
        const data = await getRecentSessions(7);
        if (isMounted) {
          setRecentSessions(data || []);
        }
      } catch (error) {
        if (isMounted) {
          console.error("Error fetching recent sessions:", error);
          setRecentSessions([]);
        }
      } finally {
        if (isMounted) {
          setRecentSessionsLoading(false);
        }
      }
    };

    fetchStreak();
    fetchUpcomingReview();
    fetchOverview();
    fetchDailyProgress();
    fetchRecentSessions();

    return () => {
      isMounted = false;
    };
  }, [streakMonth.year, streakMonth.month]);

  const handleMonthChange = (delta) => {
    setStreakMonth((prev) => {
      const updated = new Date(prev.year, prev.month - 1 + delta, 1);
      return {
        year: updated.getFullYear(),
        month: updated.getMonth() + 1,
      };
    });
  };

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <h2>Thống kê kết quả học tập</h2>
        </div>

        {/* <div className={styles.headerRight}>
          <button className={styles.exportBtn}>Xuất báo cáo</button>
        </div> */}
      </div>


      {/* Summary Cards */}
      <div className={styles.summaryGrid}>
        {/* Tổng từ đã học */}
        <div className={styles.card}>
          <div className={styles.cardTop}>
            <div className={`${styles.iconBox} ${styles.iconBlue}`}>
              <BookOpen size={18} />
            </div>
            <h4>Tổng từ đã học</h4>
          </div>
          <p className={styles.number}>
            {overviewLoading ? "..." : overview.totalLearnedCount.toLocaleString()}
          </p>
          <span className={styles.change}>Từ trước đến nay</span>
        </div>

        {/* Từ mới hôm nay */}
        <div className={styles.card}>
          <div className={styles.cardTop}>
            <div className={`${styles.iconBox} ${styles.iconGreen}`}>
              <Plus size={18} />
            </div>
            <h4>Từ mới hôm nay</h4>
          </div>
          <p className={styles.number}>
            {overviewLoading ? "..." : overview.newWordsToday.toLocaleString()}
          </p>
          <span className={styles.goal}>Đã học trong ngày</span>
        </div>

        {/* Ôn tập hôm nay */}
        <div className={styles.card}>
          <div className={styles.cardTop}>
            <div className={`${styles.iconBox} ${styles.iconPurple}`}>
              <RotateCcw size={18} />
            </div>
            <h4>Ôn tập hôm nay</h4>
          </div>
          <p className={styles.number}>
            {overviewLoading ? "..." : overview.overdueAndDueTodayNotReviewed.toLocaleString()}
          </p>
          <span className={styles.change}>Từ cần ôn tập</span>
        </div>

        {/* Từ đã ôn tập */}
        <div className={styles.card}>
          <div className={styles.cardTop}>
            <div className={`${styles.iconBox} ${styles.iconOrange}`}>
              <CheckCircle size={18} />
            </div>
            <h4>Từ đã ôn tập</h4>
          </div>
          <p className={styles.number}>
            {overviewLoading ? "..." : overview.dueTodayAndReviewed.toLocaleString()}
          </p>
          <span className={styles.streak}>Đã hoàn thành hôm nay</span>
        </div>
      </div>

      {/* Progress + Streak Calendar */}
      <div className={styles.mainTwoCol}>
        <div className={styles.leftCol}>
          <StreakCalendar
            data={streakData}
            month={streakMonth}
            isLoading={streakLoading}
            error={streakError}
            onPrevMonth={() => handleMonthChange(-1)}
            onNextMonth={() => handleMonthChange(1)}
          />
          <ProgressChart data={dailyProgressLoading ? [] : dailyProgress} />
        </div>

        <div className={styles.rightCol}>
          <UpcomingReview 
            data={upcomingReviewData} 
            isLoading={upcomingReviewLoading}
            error={upcomingReviewError}
          />
        </div>
      </div>
      <RecentVocabulary data={recentSessionsLoading ? [] : recentSessions} />

    </div>
  );
};

export default StatisticsPage;
