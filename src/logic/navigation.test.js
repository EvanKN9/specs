import test from 'node:test'
import assert from 'node:assert/strict'
import { navigateWorkflow, replacementDraftFor } from './navigation.js'

const state = { page: 'recommendation', history: ['home'], future: ['updated'], openPanel: 'compatibility', pickerCategory: null, currentBuild: { id: 'build-1' }, replacementDraft: { category: 'gpu', candidateId: 'gpu-2' } }

test('workflow navigation closes blocking panels without losing the build or draft', () => {
  const next = navigateWorkflow(state, 'preferences')
  assert.equal(next.page, 'preferences')
  assert.equal(next.openPanel, null)
  assert.equal(next.currentBuild.id, 'build-1')
  assert.deepEqual(next.replacementDraft, state.replacementDraft)
  assert.deepEqual(next.history, ['home', 'recommendation'])
  assert.deepEqual(next.future, [])
})

test('reopening the same replacement step preserves its candidate', () => {
  assert.deepEqual(replacementDraftFor(state, 'gpu'), state.replacementDraft)
  assert.deepEqual(replacementDraftFor(state, 'cpu'), { category: 'cpu', candidateId: null })
})
