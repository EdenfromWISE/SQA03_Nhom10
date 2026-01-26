import React, { useState, useEffect, useMemo, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import styles from './CourseListPage.module.css';
import ContentCard from '../components/ContentCard/ContentCard';
import { env } from '../config/env';
import { useDocumentTitle } from '../hooks/useDocumentTitle';

function CourseListPage() { 
  useDocumentTitle('Khóa học');
  const [myCourses, setMyCourses] = useState([]);
  const [allCourses, setAllCourses] = useState([]);
  const [query, setQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState(null);
  const [showAllMy, setShowAllMy] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const searchTimeoutRef = useRef(null);
  const searchWrapRef = useRef(null);

  const navigate = useNavigate();

  /* --------------------------- FETCH COURSES --------------------------- */
  useEffect(() => {
    const fetchData = async () => {
      const token =
        localStorage.getItem('accessToken') ||
        sessionStorage.getItem('accessToken');

      if (!token) {
        navigate('/login');
        return;
      }

      try {
        const res = await axios.get(env.API_ENDPOINTS.VOCABULARY.COURSES, {
          headers: { Authorization: `Bearer ${token}` },
        });

        const data = res.data || [];
        setAllCourses(data);
        setMyCourses(data.filter(c => c.is_favorite));
      } catch (error) {
        console.error('Error fetching courses', error);
        navigate('/login');
      }
    };

    fetchData();
  }, [navigate]);

  /* --------------------------- TOGGLE FAVORITE --------------------------- */
  const toggleFavorite = async (courseId) => {
    const token =
      localStorage.getItem('accessToken') ||
      sessionStorage.getItem('accessToken');

    if (!token) return;

    try {
      const res = await axios.patch(
        env.API_ENDPOINTS.VOCABULARY.COURSE_FAVORITE(courseId),
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const updated = res.data;

      // Update allCourses
      setAllCourses(prev =>
        prev.map(c => (c.id === courseId ? updated : c))
      );

      // Update myCourses
      setMyCourses(prev => {
        if (updated.is_favorite) {
          if (!prev.some(x => x.id === updated.id)) return [...prev, updated];
          return prev.map(x => (x.id === updated.id ? updated : x));
        } else {
          return prev.filter(c => c.id !== updated.id);
        }
      });
    } catch (error) {
      console.error('Error toggling favorite', error);
    }
  };

  /* --------------------------- VOCABULARY SEARCH --------------------------- */
  useEffect(() => {
    // Clear previous timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    // If query is empty, clear results
    if (!query.trim()) {
      setSearchResults([]);
      setShowResults(false);
      setIsSearching(false);
      return;
    }

    // Set searching state
    setIsSearching(true);
    setShowResults(true);

    // Debounce search
    searchTimeoutRef.current = setTimeout(async () => {
      const token =
        localStorage.getItem('accessToken') ||
        sessionStorage.getItem('accessToken');

      if (!token) {
        setIsSearching(false);
        return;
      }

      try {
        const res = await axios.get(env.API_ENDPOINTS.VOCABULARY.SEARCH, {
          params: { q: query, limit: 20 },
          headers: { Authorization: `Bearer ${token}` },
        });
        setSearchResults(res.data || []);
      } catch (error) {
        console.error('Error searching vocabularies', error);
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [query]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchWrapRef.current && !searchWrapRef.current.contains(event.target)) {
        setShowResults(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleVocabClick = (vocab) => {
    navigate(`/topic/${vocab.topic_id}`);
    setQuery('');
    setShowResults(false);
  };

  /* --------------------------- FILTER --------------------------- */
  const filterByQueryAndCategory = (courses) => {
    let result = courses;

    if (activeCategory) {
      result = result.filter(c =>
        Array.isArray(c.topics) &&
        c.topics.some(t =>
          (t || '').toLowerCase().includes(activeCategory.toLowerCase())
        )
      );
    }

    // Note: query is now used for vocabulary search, not course filtering
    return result;
  };

  const filteredMyCourses = useMemo(
    () => filterByQueryAndCategory(myCourses),
    [myCourses, activeCategory]
  );

  const filteredAllCourses = useMemo(
    () => filterByQueryAndCategory(allCourses),
    [allCourses, activeCategory]
  );

  /* --------------------------- UI RENDER --------------------------- */
  return (
    <div className={styles.pageWrap}>
      
      {/* HEADER */}
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Khóa học</h1>
          <p className={styles.subTitle}>Chọn một bộ từ vựng phù hợp và bắt đầu luyện tập mỗi ngày.</p>
        </div>

        <div className={styles.searchWrap} ref={searchWrapRef}>
          <div className={styles.searchContainer}>
            <input
              className={styles.searchInput}
              placeholder="Tìm từ vựng"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onFocus={() => query.trim() && setShowResults(true)}
            />
            {showResults && query.trim() && (
              <div className={styles.searchResults}>
                {isSearching ? (
                  <div className={styles.searchLoading}>Đang tìm kiếm...</div>
                ) : searchResults.length > 0 ? (
                  <>
                    <div className={styles.searchResultsHeader}>
                      Tìm thấy {searchResults.length} từ vựng
                    </div>
                    {searchResults.map((vocab) => (
                      <div
                        key={vocab.id}
                        className={styles.searchResultItem}
                        onClick={() => handleVocabClick(vocab)}
                      >
                        <div className={styles.searchResultWord}>
                          <strong>{vocab.word}</strong>
                          {vocab.pronunciation && (
                            <span className={styles.searchResultPronunciation}>
                              {vocab.pronunciation}
                            </span>
                          )}
                        </div>
                        <div className={styles.searchResultMeaning}>{vocab.meaning}</div>
                        <div className={styles.searchResultMeta}>
                          {vocab.topic_title} • {vocab.course_title}
                        </div>
                      </div>
                    ))}
                  </>
                ) : (
                  <div className={styles.searchNoResults}>
                    Không tìm thấy từ vựng nào
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </header>

      {/* MY COURSES (3 + XEM THÊM) */}
      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <h3>Khóa học của bạn</h3>
        </div>

        <div className={styles.gridCourses}>
          {(showAllMy ? filteredMyCourses : filteredMyCourses.slice(0, 3))
            .map(c => (
              <ContentCard
                key={c.id}
                to={`/course/${c.id}`}
                imageUrl={c.image_url}
                title={c.title}
                meta={`${Array.isArray(c.topics) ? c.topics.length : 0} chủ đề`}
                isFavorite={c.is_favorite}
                showFavorite={true}
                onFavoriteClick={() => toggleFavorite(c.id)}
                progressStatus={c.progress_status}
              />
            ))}

          {filteredMyCourses.length === 0 && (
            <div className={styles.emptyText}>
              Bạn chưa có khóa học yêu thích. Thêm vài khóa nhé!
            </div>
          )}
        </div>

        {filteredMyCourses.length > 3 && (
          <div className={styles.viewMoreWrap}>
            <button
              className={styles.viewMoreBtn}
              onClick={() => setShowAllMy(!showAllMy)}
            >
              {showAllMy ? "<< Rút gọn" : "Xem thêm >>"}
            </button>
          </div>
        )}
      </section>

      {/* ALL COURSES */}
      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <h3>Tất cả khóa học</h3>
        </div>

        <div className={styles.gridCourses}>
          {filteredAllCourses.length > 0 ? (
            filteredAllCourses.map(c => (
              <ContentCard
                key={c.id}
                to={`/course/${c.id}`}
                imageUrl={c.image_url}
                title={c.title}
                meta={`${Array.isArray(c.topics) ? c.topics.length : 0} chủ đề`}
                isFavorite={c.is_favorite}
                showFavorite={true}
                onFavoriteClick={() => toggleFavorite(c.id)}
                progressStatus={c.progress_status}
              />
            ))
          ) : (
            <div className={styles.emptyText}>Không tìm thấy khóa học phù hợp.</div>
          )}
        </div>
      </section>

    </div>
  );
}

export default CourseListPage;
