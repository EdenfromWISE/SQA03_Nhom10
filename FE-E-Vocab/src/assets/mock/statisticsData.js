// /src/assets/mock/statisticsData.js

export const statisticsData = {
  summary: {
    totalWords: 1247,
    newWordsToday: 12,
    dailyGoal: 15,
    retentionRate: 87,
    streakDays: 15,
    change: {
      totalWords: "+23 từ tuần này",
      retentionRate: "+5% so với tuần trước",
    },
  },
  progress: [
    { day: "T2", words: 5 },
    { day: "T3", words: 8 },
    { day: "T4", words: 12 },
    { day: "T5", words: 15 },
    { day: "T6", words: 12 },
    { day: "T7", words: 18 },
    { day: "CN", words: 6 },
  ],
  achievements: [
    {
      id: 1,
      title: "Chuyên cần",
      desc: "Học 7 ngày liên tiếp",
      locked: false,
    },
    {
      id: 2,
      title: "500 từ vựng",
      desc: "Hoàn thành 500 từ vựng",
      locked: false,
    },
    {
      id: 3,
      title: "7 ngày liên tục",
      desc: "Streak 7 ngày hoàn hảo",
      locked: false,
    },
    {
      id: 4,
      title: "1000 từ vựng",
      desc: "Tiếp tục phấn đấu (247/1000)",
      locked: true,
    },
  ],

  recentVocab: [
    {
      time: "Hôm nay, 14:30",
      type: "Học từ vựng",
      wordsCount: 15,
      result: "87%",
      status: "Hoàn thành",
      learnedAt: "Hôm nay",
    },
    {
      time: "Hôm qua, 20:15",
      type: "Ôn tập",
      wordsCount: 12,
      result: "92%",
      status: "Hoàn thành",
      learnedAt: "Hôm qua",
    },
    {
      time: "2 ngày trước, 19:00",
      type: "Học từ vựng",
      wordsCount: 18,
      result: "78%",
      status: "Hoàn thành",
      learnedAt: "2 ngày trước",
    },
  ],
  courses: [
    { name: "Cơ bản", progress: 80, color: "#86efac" },
    { name: "Trung cấp", progress: 60, color: "#fde68a" },
    { name: "Nâng cao", progress: 40, color: "#93c5fd" },
    { name: "Phát âm", progress: 70, color: "#fca5a5" },
    { name: "Từ vựng chuyên sâu", progress: 55, color: "#a78bfa" },
  ],
};
