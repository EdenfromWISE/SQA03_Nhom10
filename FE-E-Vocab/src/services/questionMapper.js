/**
 * Question Mapper - Map dữ liệu câu hỏi từ backend sang frontend format
 */

/**
 * Map question type từ backend sang frontend
 */
const QUESTION_TYPE_MAP = {
  listening: 'audio_multiple_choice',
  reading: 'definition_to_word',
  writing: 'definition_to_input',
  matching: 'word_definition_matching',
  speaking: 'pronunciation'
};

/**
 * Map một câu hỏi từ backend format sang frontend format
 * @param {object} backendQuestion - Câu hỏi từ backend
 * @returns {object} Câu hỏi ở frontend format
 */
export const mapQuestion = (backendQuestion) => {
  const { id, type, content, order } = backendQuestion;
  const frontendType = QUESTION_TYPE_MAP[type] || type;

  // Base structure
  const mapped = {
    id,
    type: frontendType,
    title: content.title || '',
    order
  };

  // Map specific fields dựa trên loại câu hỏi
  switch (type) {
    case 'listening': {
      // Backend: { prompt: { word, audio_url, pronunciation, options } }
      // Frontend: { audio_url, options, correct_answer, explanation }
      mapped.word = content.prompt?.word || '';
      mapped.audio_url = content.prompt?.audio_url || '';
      mapped.pronunciation = content.prompt?.pronunciation || '';
      mapped.options = content.prompt?.options || [];
      break;
    }

    case 'reading': {
      // Backend: { prompt: { definition, options } }
      // Frontend: { definition, options, correct_answer, explanation }
      mapped.definition = content.prompt?.definition || '';
      mapped.options = content.prompt?.options || [];
      mapped.example_vi = content.prompt?.example_vi || '';
      break;
    }

    case 'writing': {
      // Backend: { prompt: { definition, hint } }
      // Frontend: { definition, hint, correct_answer, alternative_answers, explanation }
      mapped.definition = content.prompt?.definition || '';
      mapped.hint = content.prompt?.hint || '';
      mapped.example_vi = content.prompt?.example_vi || '';
      break;
    }

    case 'matching': {
      // Backend: { prompt: { words, definitions } }
      // Frontend: { words, definitions, correct_answer, explanation }
      mapped.words = content.prompt?.words || [];
      mapped.definitions = content.prompt?.definitions || [];
      break;
    }

    case 'speaking': {
      // Backend: { prompt: { definition, word, target_word, pronunciation, audio_url } }
      // Frontend: { definition, word, target_word, pronunciation, audio_url, explanation }
      mapped.definition = content.prompt?.definition || '';
      mapped.word = content.prompt?.word || content.prompt?.target_word || '';
      mapped.target_word = content.prompt?.target_word || content.prompt?.word || '';
      mapped.pronunciation = content.prompt?.pronunciation || '';
      mapped.audio_url = content.prompt?.audio_url || '';
      break;
    }

    default:
      // Giữ nguyên content nếu không match
      Object.assign(mapped, content);
  }

  return mapped;
};

/**
 * Map danh sách câu hỏi từ backend sang frontend
 * @param {array} backendQuestions - Danh sách câu hỏi từ backend
 * @returns {array} Danh sách câu hỏi ở frontend format
 */
export const mapQuestions = (backendQuestions) => {
  if (!Array.isArray(backendQuestions)) {
    return [];
  }
  return backendQuestions.map(mapQuestion);
};

/**
 * Map câu trả lời từ frontend sang backend format
 * @param {string} questionType - Loại câu hỏi (backend type)
 * @param {any} answer - Câu trả lời từ frontend
 * @returns {any} Câu trả lời ở backend format
 */
export const mapAnswerToBackend = (questionType, answer) => {
  switch (questionType) {
    case 'listening':
    case 'reading':
      // Frontend gửi index, backend nhận index
      return answer;

    case 'writing':
      // Frontend gửi string, backend nhận string
      return answer;

    case 'matching':
      // Frontend: [{ word: 'hello', definition: 'xin chào' }, ...]
      // Backend: { 'hello': 'xin chào', ... }
      if (Array.isArray(answer)) {
        return answer.reduce((acc, pair) => {
          acc[pair.word] = pair.definition;
          return acc;
        }, {});
      }
      return answer;

    // case 'speaking':
    //   // Speaking gửi pronunciation_score riêng, không qua answer
    //   return answer;

    default:
      return answer;
  }
};

/**
 * Lấy backend question type từ frontend type
 * @param {string} frontendType - Frontend question type
 * @returns {string} Backend question type
 */
export const getBackendType = (frontendType) => {
  const reversed = Object.entries(QUESTION_TYPE_MAP).find(
    ([_, value]) => value === frontendType
  );
  return reversed ? reversed[0] : frontendType;
};

export default {
  mapQuestion,
  mapQuestions,
  mapAnswerToBackend,
  getBackendType
};

