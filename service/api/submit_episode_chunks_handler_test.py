# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3
"""Tests for submit_episode_chunks_handler."""
import time
from unittest import mock

from absl.testing import absltest
from absl.testing import parameterized
from api import data_cache
from api import model_selector
from api import submit_episode_chunks_handler
from data_store import assignment_monitor
from data_store import data_store
from data_store import file_system
from data_store import resource_id

# pylint: disable=g-bad-import-order
import common.generate_protos  # pylint: disable=unused-import
import action_pb2
import data_store_pb2
import episode_pb2
import observation_pb2
import falken_service_pb2
import session_pb2
from google.rpc import code_pb2
from learner.brains import specs


class SubmitEpisodeChunksHandlerTest(parameterized.TestCase):

  def setUp(self):
    super().setUp()
    self._file_system = file_system.FakeFileSystem()
    self._data_store = data_store.DataStore(self._file_system)
    self._default_hyperparameters = (
        submit_episode_chunks_handler.FLAGS.hyperparameters)
    self._ep_resource_id = resource_id.FalkenResourceId(
        'projects/p0/brains/b0/sessions/s0/episodes/ep0')
    self._session_resource_id = resource_id.FalkenResourceId(
        'projects/p0/brains/b0/sessions/s0')

  def tearDown(self):
    submit_episode_chunks_handler.FLAGS.hyperparameters = (
        self._default_hyperparameters)
    super().tearDown()

  def _chunks(self, include_steps=True):
    steps = []
    if include_steps:
      steps = [
          episode_pb2.Step(
              observation=observation_pb2.ObservationData(),
              action=action_pb2.ActionData(
                  source=action_pb2.ActionData.HUMAN_DEMONSTRATION))
      ]
    return [
        episode_pb2.EpisodeChunk(
            episode_id='ep0',
            chunk_id=0,
            steps=steps,
            episode_state=episode_pb2.IN_PROGRESS,
            model_id='m0')
    ]

  def _data_store_chunk(self, created_micros=0):
    return data_store_pb2.EpisodeChunk(
        project_id='p0',
        brain_id='b0',
        session_id='s0',
        episode_id='ep0',
        data=self._chunks()[0],
        created_micros=created_micros,
        steps_type=data_store_pb2.ONLY_DEMONSTRATIONS)

  @mock.patch.object(submit_episode_chunks_handler,
                     '_check_episode_data_with_brain_spec')
  @mock.patch.object(submit_episode_chunks_handler, '_store_episode_chunks')
  @mock.patch.object(submit_episode_chunks_handler, '_try_start_assignments')
  @mock.patch.object(model_selector, 'ModelSelector')
  def test_submit_episode_chunks(self, selector, unused_try, unused_store,
                                 unused_check):
    mock_ds = mock.Mock()
    mock_ds.resource_id_from_proto_ids.return_value = self._session_resource_id
    mock_selector = selector.return_value
    type(mock_selector).session_progress = mock.PropertyMock(return_value=0.5)
    mock_selector.get_training_state.return_value = (
        session_pb2.SessionInfo.TRAINING)
    mock_selector.select_next_model.return_value = resource_id.FalkenResourceId(
        project='p0', brain='b0', session='s0', model='m0')
    self.assertEqual(
        submit_episode_chunks_handler.submit_episode_chunks(
            falken_service_pb2.SubmitEpisodeChunksRequest(), mock.Mock(),
            mock_ds, mock.Mock()),
        falken_service_pb2.SubmitEpisodeChunksResponse(
            session_info=session_pb2.SessionInfo(
                model_id='m0', state=session_pb2.SessionInfo.TRAINING,
                training_progress=0.5)))

  @mock.patch.object(submit_episode_chunks_handler,
                     '_check_episode_data_with_brain_spec')
  def test_submit_episode_chunks_check_fails(self, check_episode_data):
    mock_context = mock.Mock()
    mock_context.abort.side_effect = Exception()
    check_episode_data.side_effect = specs.TypingError('Failure.')
    with self.assertRaises(Exception):
      submit_episode_chunks_handler.submit_episode_chunks(
          falken_service_pb2.SubmitEpisodeChunksRequest(),
          mock_context, None, None)
    mock_context.abort.assert_called_once_with(
        code_pb2.INVALID_ARGUMENT,
        'Episode data failed did not match the brain spec for the session. '
        'Failure.')
    check_episode_data.assert_called_once_with(None, '', '', mock.ANY)
    self.assertEmpty(check_episode_data.call_args[0][3])

  @mock.patch.object(submit_episode_chunks_handler,
                     '_check_episode_data_with_brain_spec')
  @mock.patch.object(submit_episode_chunks_handler,
                     '_store_episode_chunks')
  def test_submit_episode_chunks_storing_fails(
      self, store_episode_chunks, check_episode_data):
    mock_context = mock.Mock()
    mock_context.abort.side_effect = Exception()
    store_episode_chunks.side_effect = ValueError('Value error.')
    request = falken_service_pb2.SubmitEpisodeChunksRequest(
        project_id='p0', brain_id='b0', session_id='s0',
        chunks=[episode_pb2.EpisodeChunk(episode_id='ep0')])
    mock_ds = mock.Mock()
    mock_ds.resource_id_from_proto_ids.return_value = self._session_resource_id
    with self.assertRaises(Exception):
      submit_episode_chunks_handler.submit_episode_chunks(
          request, mock_context, mock_ds, mock.Mock())
    mock_context.abort.assert_called_once_with(
        code_pb2.INVALID_ARGUMENT,
        f'Storing episode chunks failed for {self._session_resource_id}. ' +
        'Value error.')
    check_episode_data.assert_called_once_with(mock_ds, 'p0', 'b0',
                                               request.chunks)
    store_episode_chunks.assert_called_once_with(
        mock_ds, request.chunks, resource_id.FalkenResourceId(
            'projects/p0/brains/b0/sessions/s0'))
    mock_ds.resource_id_from_proto_ids.assert_called_once_with(
        project_id=request.project_id, brain_id=request.brain_id,
        session_id=request.session_id)

  @mock.patch.object(submit_episode_chunks_handler,
                     '_check_episode_data_with_brain_spec')
  @mock.patch.object(submit_episode_chunks_handler,
                     '_store_episode_chunks')
  @mock.patch.object(submit_episode_chunks_handler, '_try_start_assignments')
  def test_submit_episode_chunks_start_assignment_fails(
      self, try_start_assignments, store_episode_chunks, check_episode_data):
    mock_context = mock.Mock()
    mock_context.abort.side_effect = Exception()
    try_start_assignments.side_effect = FileNotFoundError(
        'Assignment not found.')
    request = falken_service_pb2.SubmitEpisodeChunksRequest(
        project_id='p0', brain_id='b0', session_id='s0',
        chunks=[episode_pb2.EpisodeChunk(episode_id='ep0')])
    mock_ds = mock.Mock()
    mock_ds.resource_id_from_proto_ids.return_value = self._session_resource_id
    with self.assertRaises(Exception):
      submit_episode_chunks_handler.submit_episode_chunks(
          request, mock_context, mock_ds, mock.Mock())
    mock_context.abort.assert_called_once_with(
        code_pb2.NOT_FOUND,
        f'Starting assignment failed for {self._session_resource_id}. ' +
        'Assignment not found.')
    check_episode_data.assert_called_once_with(
        mock_ds, 'p0', 'b0', request.chunks)
    store_episode_chunks.assert_called_once_with(
        mock_ds, request.chunks, self._session_resource_id)
    try_start_assignments.assert_called_once_with(
        mock_ds, mock.ANY, self._session_resource_id,
        store_episode_chunks.return_value, request.chunks)
    mock_ds.resource_id_from_proto_ids.assert_called_once_with(
        project_id=request.project_id, brain_id=request.brain_id,
        session_id=request.session_id)

  @mock.patch.object(submit_episode_chunks_handler,
                     '_check_episode_data_with_brain_spec')
  @mock.patch.object(submit_episode_chunks_handler, '_store_episode_chunks')
  @mock.patch.object(submit_episode_chunks_handler, '_try_start_assignments')
  @mock.patch.object(model_selector, 'ModelSelector')
  def test_submit_episode_chunks_select_model_fails(self, selector,
                                                    try_start_assignments,
                                                    store_episode_chunks,
                                                    check_episode_data):
    mock_context = mock.Mock()
    mock_context.abort.side_effect = Exception()
    mock_selector = selector.return_value
    mock_selector.get_training_state.return_value = (
        session_pb2.SessionInfo.TRAINING)
    mock_selector.select_next_model.side_effect = ValueError(
        'Evaluation not found for session.')
    request = falken_service_pb2.SubmitEpisodeChunksRequest(
        project_id='p0',
        brain_id='b0',
        session_id='s0',
        chunks=[episode_pb2.EpisodeChunk(episode_id='ep0')])
    mock_ds = mock.Mock()
    mock_ds.resource_id_from_proto_ids.return_value = self._session_resource_id

    with self.assertRaises(Exception):
      submit_episode_chunks_handler.submit_episode_chunks(
          request, mock_context, mock_ds, mock.Mock())
    mock_context.abort.assert_called_once_with(
        code_pb2.INVALID_ARGUMENT,
        'Failed to select model for session projects/p0/brains/b0/sessions/s0. '
        'Evaluation not found for session.')
    check_episode_data.assert_called_once_with(mock_ds, 'p0', 'b0',
                                               request.chunks)
    store_episode_chunks.assert_called_once_with(mock_ds, request.chunks,
                                                 self._session_resource_id)
    try_start_assignments.assert_called_once_with(
        mock_ds, mock.ANY, self._session_resource_id,
        store_episode_chunks.return_value, request.chunks)
    mock_ds.resource_id_from_proto_ids.assert_called_once_with(
        project_id=request.project_id,
        brain_id=request.brain_id,
        session_id=request.session_id)

  @mock.patch.object(data_cache, 'get_brain_spec')
  def test_check_episode_data_with_brain_spec_empty_in_progress(
      self, get_brain_spec):
    mock_ds = mock.Mock()
    get_brain_spec.return_value = mock.Mock()
    chunks = self._chunks(False)
    with self.assertRaisesWithLiteralMatch(
        specs.TypingError,
        'Received an empty chunk that does not close the episode at '
        'chunk_index: 0.'):
      submit_episode_chunks_handler._check_episode_data_with_brain_spec(
          mock_ds, 'p0', 'b0', chunks)
    get_brain_spec.assert_called_once_with(mock_ds, 'p0', 'b0')

  @mock.patch.object(data_cache, 'get_brain_spec')
  def test_check_episode_data_with_brain_spec_empty_at_id_0(
      self, get_brain_spec):
    mock_ds = mock.Mock()
    get_brain_spec.return_value = mock.Mock()
    chunks = self._chunks(False)
    chunks[0].episode_state = episode_pb2.FAILURE

    with self.assertRaisesWithLiteralMatch(
        specs.TypingError, 'Received an empty episode at chunk_index: 0.'):
      submit_episode_chunks_handler._check_episode_data_with_brain_spec(
          mock_ds, 'p0', 'b0', chunks)
    get_brain_spec.assert_called_once_with(mock_ds, 'p0', 'b0')

  @parameterized.named_parameters(
      ('action', 'action_spec'),
      ('observation', 'observation_spec'))
  @mock.patch.object(specs, 'BrainSpec')
  @mock.patch.object(data_cache, 'get_brain_spec')
  def test_check_episode_data_with_brain_spec_check_fails(
      self, field, get_brain_spec, brain_spec_proto_node):
    mock_ds = mock.Mock()
    get_brain_spec.return_value = mock.Mock()
    chunks = self._chunks()
    mock_brain_spec_node = mock.Mock()
    brain_spec_proto_node.return_value = mock_brain_spec_node
    getattr(mock_brain_spec_node,
            field).proto_node.data_to_proto_nest.side_effect = (
                specs.TypingError('data_to_proto_nest failed.'))

    with self.assertRaisesWithLiteralMatch(
        specs.TypingError,
        'Brainspec check failed in chunk 0, step 0: data_to_proto_nest '
        'failed.'):
      submit_episode_chunks_handler._check_episode_data_with_brain_spec(
          mock_ds, 'p0', 'b0', chunks)

    get_brain_spec.assert_called_once_with(mock_ds, 'p0', 'b0')
    mock_brain_spec_node.action_spec.proto_node.data_to_proto_nest.assert_called_once_with(
        chunks[0].steps[0].action)
    if field == 'observation_spec':
      (mock_brain_spec_node.observation_spec.proto_node.data_to_proto_nest
       .assert_called_once_with(chunks[0].steps[0].observation))
    brain_spec_proto_node.assert_called_once_with(get_brain_spec.return_value)

  @mock.patch.object(submit_episode_chunks_handler, '_record_online_evaluation')
  @mock.patch.object(submit_episode_chunks_handler, '_get_steps_type')
  @mock.patch.object(submit_episode_chunks_handler, '_merge_steps_types')
  @mock.patch.object(time, 'time')
  def test_store_episode_chunks(
      self,
      mock_time,
      merge_steps_type,
      get_steps_type,
      record_online_evaluation):
    mock_ds = mock.Mock()
    mock_ds.resource_id_from_proto_ids.return_value = (
        self._ep_resource_id)

    mock_time.return_value = 1

    chunks = self._chunks()
    merge_steps_type.return_value = data_store_pb2.ONLY_DEMONSTRATIONS
    get_steps_type.return_value = data_store_pb2.ONLY_DEMONSTRATIONS

    self.assertEqual(
        submit_episode_chunks_handler._store_episode_chunks(
            mock_ds, chunks, self._session_resource_id),
        merge_steps_type.return_value)

    mock_ds.write.assert_called_once_with(
        data_store_pb2.EpisodeChunk(
            project_id='p0',
            brain_id='b0',
            session_id='s0',
            episode_id='ep0',
            chunk_id=0,
            created_micros=1_000_000,
            data=chunks[0],
            steps_type=get_steps_type.return_value))

    mock_ds.update_session_data_timestamps.assert_called_once_with(
        self._session_resource_id,
        1_000_000,
        True)

    record_online_evaluation.assert_called_once_with(
        mock_ds, self._data_store_chunk(1_000_000), self._ep_resource_id)
    get_steps_type.assert_called_once_with(chunks[0])

  @mock.patch.object(submit_episode_chunks_handler, '_get_steps_type')
  def test_store_episode_chunks_failure_at_get_steps_type(self, get_steps_type):
    mock_ds = mock.Mock()
    chunks = self._chunks()
    get_steps_type.side_effect = ValueError('Unsupported step type.')

    with self.assertRaisesWithLiteralMatch(
        ValueError,
        'Encountered error while getting steps type for episode ep0 chunk 0. '
        'Unsupported step type.'):
      submit_episode_chunks_handler._store_episode_chunks(
          mock_ds, chunks, self._ep_resource_id)

    mock_ds.write.assert_not_called()
    get_steps_type.assert_called_once_with(chunks[0])

  @mock.patch.object(submit_episode_chunks_handler, '_record_online_evaluation')
  @mock.patch.object(submit_episode_chunks_handler, '_get_steps_type')
  @mock.patch.object(time, 'time')
  def test_store_episode_chunks_failure_at_record_online_evaluation(
      self, mock_time, get_steps_type, record_online_evaluation):
    mock_ds = mock.Mock()
    mock_ds.resource_id_from_proto_ids.return_value = self._ep_resource_id
    chunks = self._chunks()
    get_steps_type.return_value = data_store_pb2.ONLY_DEMONSTRATIONS
    record_online_evaluation.side_effect = ValueError('Episode incomplete.')

    mock_time.return_value = 1

    with self.assertRaisesWithLiteralMatch(
        ValueError,
        'Encountered error while recording online evaluation for episode ep0 '
        'chunk 0. Episode incomplete.'):
      submit_episode_chunks_handler._store_episode_chunks(
          mock_ds, chunks, self._session_resource_id)

    mock_ds.write.assert_called_once_with(
        data_store_pb2.EpisodeChunk(
            project_id='p0',
            brain_id='b0',
            session_id='s0',
            episode_id='ep0',
            chunk_id=0,
            created_micros=1_000_000,
            data=chunks[0],
            steps_type=get_steps_type.return_value))

    mock_ds.update_session_data_timestamps.assert_called_once_with(
        self._session_resource_id,
        1_000_000,
        True)

    record_online_evaluation.assert_called_once_with(
        mock_ds, self._data_store_chunk(1_000_000), self._ep_resource_id)
    get_steps_type.assert_called_once_with(chunks[0])

  def test_get_steps_type_mixed(self):
    chunk = episode_pb2.EpisodeChunk(steps=[
        episode_pb2.Step(
            action=action_pb2.ActionData(
                source=action_pb2.ActionData.HUMAN_DEMONSTRATION)),
        episode_pb2.Step(
            action=action_pb2.ActionData(
                source=action_pb2.ActionData.BRAIN_ACTION))
    ])
    self.assertEqual(
        submit_episode_chunks_handler._get_steps_type(chunk),
        data_store_pb2.MIXED)

  def test_get_steps_type_only_demos(self):
    chunk = episode_pb2.EpisodeChunk(steps=[
        episode_pb2.Step(
            action=action_pb2.ActionData(
                source=action_pb2.ActionData.HUMAN_DEMONSTRATION))
    ])
    self.assertEqual(
        submit_episode_chunks_handler._get_steps_type(chunk),
        data_store_pb2.ONLY_DEMONSTRATIONS)

  def test_get_steps_type_only_inferences(self):
    chunk = episode_pb2.EpisodeChunk(steps=[
        episode_pb2.Step(
            action=action_pb2.ActionData(
                source=action_pb2.ActionData.NO_SOURCE)),
        episode_pb2.Step(
            action=action_pb2.ActionData(
                source=action_pb2.ActionData.BRAIN_ACTION))
    ])
    self.assertEqual(
        submit_episode_chunks_handler._get_steps_type(chunk),
        data_store_pb2.ONLY_INFERENCES)

  def test_get_steps_type_only_unknown(self):
    chunk = episode_pb2.EpisodeChunk(steps=[])
    self.assertEqual(
        submit_episode_chunks_handler._get_steps_type(chunk),
        data_store_pb2.UNKNOWN)

  def test_get_steps_type_unsupported(self):
    chunk = episode_pb2.EpisodeChunk(steps=[
        episode_pb2.Step(
            action=action_pb2.ActionData(
                source=action_pb2.ActionData.SOURCE_UNKNOWN))
    ])
    with self.assertRaisesWithLiteralMatch(ValueError,
                                           'Unsupported step type: 0'):
      submit_episode_chunks_handler._get_steps_type(chunk)

  @mock.patch.object(submit_episode_chunks_handler, '_get_episode_steps_type')
  @mock.patch.object(submit_episode_chunks_handler, '_episode_score')
  @mock.patch.object(submit_episode_chunks_handler, '_episode_complete')
  def test_record_online_evaluation(self, episode_complete, episode_score,
                                    get_episode_steps_type):
    episode_complete.return_value = True
    episode_score.return_value = 1
    get_episode_steps_type.return_value = (data_store_pb2.ONLY_INFERENCES,
                                           {'m0'})

    mock_ds = mock.Mock()
    chunk = self._chunks()[0]
    _ = submit_episode_chunks_handler._record_online_evaluation(
        mock_ds, chunk, self._ep_resource_id)
    mock_ds.write.assert_called_once_with(
        data_store_pb2.OnlineEvaluation(
            project_id=self._ep_resource_id.project,
            brain_id=self._ep_resource_id.brain,
            session_id=self._ep_resource_id.session,
            episode_id=self._ep_resource_id.episode,
            model='m0',
            score=1.0))
    episode_complete.assert_called_once_with(chunk)
    episode_score.assert_called_once_with(chunk)
    get_episode_steps_type.assert_called_once_with(
        mock_ds, chunk, self._ep_resource_id)

  @mock.patch.object(submit_episode_chunks_handler, '_episode_complete')
  def test_record_online_evaluation_failure_at_episode_complete(
      self, episode_complete):
    episode_complete.side_effect = ValueError('Unsupported episode state 0.')

    chunk = self._chunks()[0]
    with self.assertRaisesWithLiteralMatch(ValueError,
                                           'Unsupported episode state 0.'):
      submit_episode_chunks_handler._record_online_evaluation(
          mock.Mock(), chunk, mock.Mock())
    episode_complete.assert_called_once_with(chunk)

  @mock.patch.object(submit_episode_chunks_handler, '_episode_score')
  @mock.patch.object(submit_episode_chunks_handler, '_episode_complete')
  def test_record_online_evaluation_failure_at_episode_score(
      self, episode_complete, episode_score):
    episode_complete.return_value = True
    episode_score.side_effect = ValueError(
        'Incomplete episode can\'t be scored.')
    chunk = self._chunks()[0]

    with self.assertRaisesWithLiteralMatch(
        ValueError, 'Incomplete episode can\'t be scored.'):
      submit_episode_chunks_handler._record_online_evaluation(
          mock.Mock(), chunk, mock.Mock())

    episode_complete.assert_called_once_with(chunk)
    episode_score.assert_called_once_with(chunk)

  @parameterized.named_parameters(
      ('no_steps_type_no_model_ids', (None, [])),
      ('not_inference', (data_store_pb2.MIXED, ['m0', 'm1'])))
  @mock.patch.object(submit_episode_chunks_handler, '_get_episode_steps_type')
  @mock.patch.object(submit_episode_chunks_handler, '_episode_score')
  @mock.patch.object(submit_episode_chunks_handler, '_episode_complete')
  def test_record_online_evaluation_no_write(self,
                                             get_episode_steps_return_value,
                                             episode_complete, episode_score,
                                             get_episode_steps_type):
    episode_complete.return_value = True
    episode_score.return_value = 1
    get_episode_steps_type.return_value = get_episode_steps_return_value

    mock_ds = mock.Mock()
    chunk = self._chunks()[0]
    _ = submit_episode_chunks_handler._record_online_evaluation(
        mock_ds, chunk, self._ep_resource_id)
    episode_complete.assert_called_once_with(chunk)
    episode_score.assert_called_once_with(chunk)
    get_episode_steps_type.assert_called_once_with(
        mock_ds, chunk, self._ep_resource_id)
    mock_ds.write.assert_not_called()

  @parameterized.named_parameters(('success', episode_pb2.SUCCESS),
                                  ('failure', episode_pb2.FAILURE),
                                  ('gave_up', episode_pb2.GAVE_UP))
  def test_episode_complete(self, state):
    self.assertTrue(
        submit_episode_chunks_handler._episode_complete(
            data_store_pb2.EpisodeChunk(
                data=episode_pb2.EpisodeChunk(episode_state=state))))

  @parameterized.named_parameters(('in_progress', episode_pb2.IN_PROGRESS),
                                  ('unspecified', episode_pb2.UNSPECIFIED),
                                  ('aborted', episode_pb2.ABORTED))
  def test_episode_incomplete(self, state):
    self.assertFalse(
        submit_episode_chunks_handler._episode_complete(
            data_store_pb2.EpisodeChunk(
                data=episode_pb2.EpisodeChunk(episode_state=state))))

  def test_episode_complete_unsupported(self):
    with self.assertRaisesWithLiteralMatch(
        ValueError, 'Unsupported episode state 8 in episode ep0 chunk 0.'):
      submit_episode_chunks_handler._episode_complete(
          data_store_pb2.EpisodeChunk(
              data=episode_pb2.EpisodeChunk(episode_state=8),
              chunk_id=0,
              episode_id='ep0'))

  @parameterized.named_parameters(
      ('success', episode_pb2.SUCCESS, model_selector.EPISODE_SCORE_SUCCESS),
      ('failure', episode_pb2.FAILURE, model_selector.EPISODE_SCORE_FAILURE),
      ('gave_up', episode_pb2.GAVE_UP, model_selector.EPISODE_SCORE_FAILURE))
  def test_episode_score(self, state, expected_score):
    self.assertEqual(
        submit_episode_chunks_handler._episode_score(
            data_store_pb2.EpisodeChunk(
                data=episode_pb2.EpisodeChunk(episode_state=state))),
        expected_score)

  @parameterized.named_parameters(('unspecified', episode_pb2.UNSPECIFIED),
                                  ('in_progress', episode_pb2.IN_PROGRESS),
                                  ('aborted', episode_pb2.ABORTED))
  def test_episode_score_incomplete(self, state):
    with self.assertRaisesWithLiteralMatch(
        ValueError, 'Incomplete episode ep0 chunk 0 can\'t be scored.'):
      submit_episode_chunks_handler._episode_score(
          data_store_pb2.EpisodeChunk(
              data=episode_pb2.EpisodeChunk(episode_state=state),
              episode_id='ep0',
              chunk_id=0))

  @parameterized.named_parameters(
      ('used_in_inference', data_store_pb2.MIXED, {'m0'}),
      ('not_used_in_inference', data_store_pb2.ONLY_DEMONSTRATIONS, set()))
  def test_get_episode_steps_type_chunk_id_0(self, steps_type, expected_models):
    mock_ds = mock.Mock()
    chunk = self._data_store_chunk()
    chunk.steps_type = steps_type
    self.assertEqual(
        submit_episode_chunks_handler._get_episode_steps_type(
            mock_ds, chunk,
            resource_id.FalkenResourceId(
                'projects/p0/brains/b0/sessions/s0/episodes/e0')),
        (steps_type, expected_models))

  @mock.patch.object(submit_episode_chunks_handler, '_merge_steps_types')
  def test_get_episode_steps_type(self, merge_steps_types):
    mock_ds = mock.Mock()
    chunk_res_ids = [
        resource_id.FalkenResourceId(f'{self._ep_resource_id}/chunks/0'),
        resource_id.FalkenResourceId(f'{self._ep_resource_id}/chunks/1')]
    mock_ds.list_by_proto_ids.return_value = (chunk_res_ids, None)
    mock_ds.read.side_effect = [
        data_store_pb2.EpisodeChunk(
            chunk_id=0,
            data=episode_pb2.EpisodeChunk(model_id='m0', chunk_id=0),
            steps_type=data_store_pb2.ONLY_INFERENCES),
        data_store_pb2.EpisodeChunk(
            chunk_id=1,
            data=episode_pb2.EpisodeChunk(model_id='m1', chunk_id=1),
            steps_type=data_store_pb2.ONLY_INFERENCES)
    ]
    merge_steps_types.return_value = data_store_pb2.ONLY_INFERENCES
    chunk = data_store_pb2.EpisodeChunk(
        chunk_id=1,  # With chunk ID 1, expect chunk 0 and chunk 1.
        data=episode_pb2.EpisodeChunk(model_id='m2', chunk_id=2),
        steps_type=data_store_pb2.ONLY_INFERENCES)

    self.assertEqual(
        submit_episode_chunks_handler._get_episode_steps_type(
            mock_ds, chunk, self._ep_resource_id),
        (merge_steps_types.return_value, {'m2', 'm0', 'm1'}))

    mock_ds.list_by_proto_ids.assert_called_once_with(
        project_id='p0', brain_id='b0', session_id='s0', episode_id='ep0',
        chunk_id='*')
    mock_ds.read.assert_has_calls([
        mock.call(chunk_res_ids[0]),
        mock.call(chunk_res_ids[1])])

    merge_steps_types.assert_has_calls([
        mock.call(data_store_pb2.UNKNOWN, data_store_pb2.ONLY_INFERENCES),
        mock.call(data_store_pb2.ONLY_INFERENCES,
                  data_store_pb2.ONLY_INFERENCES)
    ])

  @mock.patch.object(submit_episode_chunks_handler, '_merge_steps_types')
  def test_get_episode_steps_type_count_mismatch(self, merge_steps_types):
    mock_ds = mock.Mock()
    mock_ds.list_by_proto_ids.return_value = (
        [f'{self._ep_resource_id}/chunks/0'], None)
    mock_ds.read.side_effect = [
        data_store_pb2.EpisodeChunk(
            chunk_id=0,
            data=episode_pb2.EpisodeChunk(model_id='m0', chunk_id=0),
            steps_type=data_store_pb2.ONLY_INFERENCES),
    ]
    merge_steps_types.return_value = data_store_pb2.ONLY_INFERENCES
    chunk = data_store_pb2.EpisodeChunk(
        chunk_id=2,
        data=episode_pb2.EpisodeChunk(model_id='m2', chunk_id=2),
        steps_type=data_store_pb2.ONLY_INFERENCES)

    with self.assertRaisesWithLiteralMatch(
        FileNotFoundError,
        'Did not find all previous chunks for chunk id 2, only got 1 chunks.'):
      submit_episode_chunks_handler._get_episode_steps_type(
          mock_ds, chunk, self._ep_resource_id)

    mock_ds.list_by_proto_ids.assert_called_once_with(
        project_id='p0', brain_id='b0', session_id='s0', episode_id='ep0',
        chunk_id='*')
    mock_ds.read.assert_called_once_with(f'{self._ep_resource_id}/chunks/0')
    merge_steps_types.assert_called_once_with(data_store_pb2.UNKNOWN,
                                              data_store_pb2.ONLY_INFERENCES)

  merge_step_map = {
      data_store_pb2.UNKNOWN: {
          data_store_pb2.UNKNOWN:
              data_store_pb2.UNKNOWN,
          data_store_pb2.ONLY_DEMONSTRATIONS:
              data_store_pb2.ONLY_DEMONSTRATIONS,
          data_store_pb2.ONLY_INFERENCES:
              data_store_pb2.ONLY_INFERENCES,
          data_store_pb2.MIXED:
              data_store_pb2.MIXED
      },
      data_store_pb2.ONLY_DEMONSTRATIONS: {
          data_store_pb2.UNKNOWN:
              data_store_pb2.ONLY_DEMONSTRATIONS,
          data_store_pb2.ONLY_DEMONSTRATIONS:
              data_store_pb2.ONLY_DEMONSTRATIONS,
          data_store_pb2.ONLY_INFERENCES:
              data_store_pb2.MIXED,
          data_store_pb2.MIXED:
              data_store_pb2.MIXED
      },
      data_store_pb2.ONLY_INFERENCES: {
          data_store_pb2.UNKNOWN: data_store_pb2.ONLY_INFERENCES,
          data_store_pb2.ONLY_DEMONSTRATIONS: data_store_pb2.MIXED,
          data_store_pb2.ONLY_INFERENCES: data_store_pb2.ONLY_INFERENCES,
          data_store_pb2.MIXED: data_store_pb2.MIXED
      },
      data_store_pb2.MIXED: {
          data_store_pb2.UNKNOWN: data_store_pb2.MIXED,
          data_store_pb2.ONLY_DEMONSTRATIONS: data_store_pb2.MIXED,
          data_store_pb2.ONLY_INFERENCES: data_store_pb2.MIXED,
          data_store_pb2.MIXED: data_store_pb2.MIXED
      }
  }

  @parameterized.product(
      type_left=[
          data_store_pb2.UNKNOWN, data_store_pb2.ONLY_DEMONSTRATIONS,
          data_store_pb2.ONLY_INFERENCES, data_store_pb2.MIXED
      ],
      type_right=[
          data_store_pb2.UNKNOWN, data_store_pb2.ONLY_DEMONSTRATIONS,
          data_store_pb2.ONLY_INFERENCES, data_store_pb2.MIXED
      ])
  def test_merge_steps_types(self, type_left, type_right):
    self.assertEqual(
        submit_episode_chunks_handler._merge_steps_types(type_left, type_right),
        SubmitEpisodeChunksHandlerTest.merge_step_map[type_left][type_right])

  @parameterized.named_parameters(
      ('session_type_training', session_pb2.INFERENCE,
       data_store_pb2.MIXED, False),
      ('with_demo_data', session_pb2.INTERACTIVE_TRAINING,
       data_store_pb2.MIXED, True),
      ('no_demo_data', session_pb2.INTERACTIVE_TRAINING,
       data_store_pb2.ONLY_INFERENCES, False))
  @mock.patch.object(data_cache, 'get_session_type')
  @mock.patch.object(assignment_monitor, 'AssignmentNotifier')
  def test_try_start_assignments(self, session_type, merged_steps_type,
                                 expect_write, mock_notifier_class,
                                 mock_get_session_type):
    with mock.patch.object(self._data_store, 'write') as mock_data_store_write:
      submit_episode_chunks_handler.FLAGS.hyperparameters = [
          '{"assignment_id_0": 0}', '{"assignment_id_1": 1}']
      expected_assignments = [
          data_store_pb2.Assignment(
              project_id='p0', brain_id='b0', session_id='s0',
              assignment_id='{"assignment_id_0": 0}'),
          data_store_pb2.Assignment(
              project_id='p0', brain_id='b0', session_id='s0',
              assignment_id='{"assignment_id_1": 1}')
      ]
      mock_get_session_type.return_value = session_type
      mock_notifier = mock_notifier_class(self._file_system)

      submit_episode_chunks_handler._try_start_assignments(
          self._data_store, mock_notifier, self._session_resource_id,
          merged_steps_type, self._chunks())

    if expect_write:
      mock_data_store_write.assert_has_calls(
          [mock.call(expected_assignments[0]),
           mock.call(expected_assignments[1])])

      expected_notifications = []
      for assignment in expected_assignments:
        expected_notifications.extend(
            mock.call(
                self._data_store.to_resource_id(assignment),
                self._data_store.to_resource_id(self._data_store_chunk()),
            ) for _ in self._chunks())
      mock_notifier.trigger_assignment_notification.assert_has_calls(
          expected_notifications)
    else:
      mock_data_store_write.assert_not_called()
      mock_notifier.trigger_assignment_notification.assert_not_called()

  def test_set_hyperparameters_valid(self):
    submit_episode_chunks_handler.FLAGS.hyperparameters = [
        '{"valid": "hparams"}']
    self.assertEqual(submit_episode_chunks_handler.FLAGS.hyperparameters,
                     ['{"valid": "hparams"}'])

  def test_set_hyperparameters_invalid(self):
    with self.assertRaises(submit_episode_chunks_handler.HyperparametersError):
      submit_episode_chunks_handler.FLAGS.hyperparameters = 'not json'

if __name__ == '__main__':
  absltest.main()
