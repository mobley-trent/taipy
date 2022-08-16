# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
from typing import Any, Iterable, List, Optional

from .._repository._repository import _AbstractRepository
from .._repository._repository_adapter import _RepositoryAdapter
from ..common._utils import _load_fct
from ..common.alias import TaskId
from ..data._data_manager_factory import _DataManagerFactory
from ..exceptions.exceptions import NonExistingDataNode
from ._task_model import _TaskModel
from .task import Task


class _TaskRepository(_AbstractRepository[_TaskModel, Task]):  # type: ignore
    def __init__(self, **kwargs):
        kwargs.update({"to_model_fct": self._to_model, "from_model_fct": self._from_model})
        self.repo = _RepositoryAdapter.select_base_repository()(**kwargs)

    @property
    def repository(self):
        return self.repo

    def _to_model(self, task: Task) -> _TaskModel:
        return _TaskModel(
            id=task.id,
            parent_id=task.parent_id,
            config_id=task.config_id,
            input_ids=self.__to_ids(task.input.values()),
            function_name=task._function.__name__,
            function_module=task._function.__module__,
            output_ids=self.__to_ids(task.output.values()),
        )

    def _from_model(self, model: _TaskModel) -> Task:
        return Task(
            id=TaskId(model.id),
            parent_id=model.parent_id,
            config_id=model.config_id,
            function=_load_fct(model.function_module, model.function_name),
            input=self.__to_data_nodes(model.input_ids),
            output=self.__to_data_nodes(model.output_ids),
        )

    def load(self, model_id: str) -> Task:
        return self.repo.load(model_id)

    def _load_all(self) -> List[Task]:
        return self.repo._load_all()

    def _load_all_by(self, by) -> List[Task]:
        return self.repo._load_all_by(by)

    def _save(self, entity: Task):
        return self.repo._save(entity)

    def _delete(self, entity_id: str):
        return self.repo._delete(entity_id)

    def _delete_all(self):
        return self.repo._delete_all()

    def _delete_many(self, ids: Iterable[str]):
        return self.repo._delete_many(ids)

    def _search(self, attribute: str, value: Any) -> Optional[Task]:
        return self.repo._search(attribute, value)

    @staticmethod
    def __to_ids(data_nodes):
        return [i.id for i in data_nodes]

    @staticmethod
    def __to_data_nodes(data_nodes_ids):
        data_nodes = []
        data_manager = _DataManagerFactory._build_manager()
        for _id in data_nodes_ids:
            if data_node := data_manager._get(_id):
                data_nodes.append(data_node)
            else:
                raise NonExistingDataNode(_id)
        return data_nodes
