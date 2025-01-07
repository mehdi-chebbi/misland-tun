import { defineStore } from 'pinia';

export const useIndicatorSelectionStore = defineStore('indicator_selection_store', {
  state: () => ({
    selections: "", //holds  user selections
    expansion_items: "", //holds  user selections
    note_key:"", // holds the selected indicator key to get note value
  }),
  getters: {
    getIndicatorSelections: (state) => state.selections, // get user selections
    getIndicatorNoteKey: (state) => state.note_key, // get selected indicator note key
    getExpansionItems: (state) => state.expansion_items, // get expansion items state
  },
  actions: {
    // store the user  indicator selections
    setIndicatorSelections(selections) {
      this.selections = selections
    },
    // store the expansion item state
    setExpansionItemSelections(expansion_items) {
      this.expansion_items = expansion_items
    },
    // store the note key to get the indicator notes
    setIndicatorNotes(note_key) {
      this.note_key = note_key
    },
    },
});


