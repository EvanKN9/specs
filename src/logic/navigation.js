export function navigateWorkflow(state, page, next = {}) {
  return {
    ...state,
    ...next,
    page,
    lastPage: page,
    history: state.page === page ? state.history : [...state.history, state.page],
    future: [],
    openPanel: null,
    pickerCategory: null,
  }
}

export function replacementDraftFor(state, category) {
  return state.replacementDraft?.category === category
    ? state.replacementDraft
    : { category, candidateId: null }
}
