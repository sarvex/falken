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
#
# automatically generated by the FlatBuffers compiler, do not modify

# namespace: tflite

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class SubGraph(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsSubGraph(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = SubGraph()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def SubGraphBufferHasIdentifier(cls, buf, offset, size_prefixed=False):
        return flatbuffers.util.BufferHasIdentifier(buf, offset, b"\x54\x46\x4C\x33", size_prefixed=size_prefixed)

    # SubGraph
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # SubGraph
    def Tensors(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            x = self._tab.Vector(o)
            x += flatbuffers.number_types.UOffsetTFlags.py_type(j) * 4
            x = self._tab.Indirect(x)
            from tflite.Tensor import Tensor
            obj = Tensor()
            obj.Init(self._tab.Bytes, x)
            return obj
        return None

    # SubGraph
    def TensorsLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        return self._tab.VectorLen(o) if o != 0 else 0

    # SubGraph
    def TensorsIsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        return o == 0

    # SubGraph
    def Inputs(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(flatbuffers.number_types.Int32Flags, a + flatbuffers.number_types.UOffsetTFlags.py_type(j * 4))
        return 0

    # SubGraph
    def InputsAsNumpy(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.GetVectorAsNumpy(flatbuffers.number_types.Int32Flags, o)
        return 0

    # SubGraph
    def InputsLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        return self._tab.VectorLen(o) if o != 0 else 0

    # SubGraph
    def InputsIsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        return o == 0

    # SubGraph
    def Outputs(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(flatbuffers.number_types.Int32Flags, a + flatbuffers.number_types.UOffsetTFlags.py_type(j * 4))
        return 0

    # SubGraph
    def OutputsAsNumpy(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            return self._tab.GetVectorAsNumpy(flatbuffers.number_types.Int32Flags, o)
        return 0

    # SubGraph
    def OutputsLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        return self._tab.VectorLen(o) if o != 0 else 0

    # SubGraph
    def OutputsIsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        return o == 0

    # SubGraph
    def Operators(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            x = self._tab.Vector(o)
            x += flatbuffers.number_types.UOffsetTFlags.py_type(j) * 4
            x = self._tab.Indirect(x)
            from tflite.Operator import Operator
            obj = Operator()
            obj.Init(self._tab.Bytes, x)
            return obj
        return None

    # SubGraph
    def OperatorsLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        return self._tab.VectorLen(o) if o != 0 else 0

    # SubGraph
    def OperatorsIsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        return o == 0

    # SubGraph
    def Name(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        return self._tab.String(o + self._tab.Pos) if o != 0 else None

def SubGraphStart(builder): builder.StartObject(5)
def SubGraphAddTensors(builder, tensors): builder.PrependUOffsetTRelativeSlot(0, flatbuffers.number_types.UOffsetTFlags.py_type(tensors), 0)
def SubGraphStartTensorsVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def SubGraphAddInputs(builder, inputs): builder.PrependUOffsetTRelativeSlot(1, flatbuffers.number_types.UOffsetTFlags.py_type(inputs), 0)
def SubGraphStartInputsVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def SubGraphAddOutputs(builder, outputs): builder.PrependUOffsetTRelativeSlot(2, flatbuffers.number_types.UOffsetTFlags.py_type(outputs), 0)
def SubGraphStartOutputsVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def SubGraphAddOperators(builder, operators): builder.PrependUOffsetTRelativeSlot(3, flatbuffers.number_types.UOffsetTFlags.py_type(operators), 0)
def SubGraphStartOperatorsVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def SubGraphAddName(builder, name): builder.PrependUOffsetTRelativeSlot(4, flatbuffers.number_types.UOffsetTFlags.py_type(name), 0)
def SubGraphEnd(builder): return builder.EndObject()

import tflite.Operator
import tflite.Tensor
try:
    from typing import List
except:
    pass

class SubGraphT(object):

    # SubGraphT
    def __init__(self):
        self.tensors = None  # type: List[tflite.Tensor.TensorT]
        self.inputs = None  # type: List[int]
        self.outputs = None  # type: List[int]
        self.operators = None  # type: List[tflite.Operator.OperatorT]
        self.name = None  # type: str

    @classmethod
    def InitFromBuf(cls, buf, pos):
        subGraph = SubGraph()
        subGraph.Init(buf, pos)
        return cls.InitFromObj(subGraph)

    @classmethod
    def InitFromObj(cls, subGraph):
        x = SubGraphT()
        x._UnPack(subGraph)
        return x

    # SubGraphT
    def _UnPack(self, subGraph):
        if subGraph is None:
            return
        if not subGraph.TensorsIsNone():
            self.tensors = []
            for i in range(subGraph.TensorsLength()):
                if subGraph.Tensors(i) is None:
                    self.tensors.append(None)
                else:
                    tensor_ = tflite.Tensor.TensorT.InitFromObj(subGraph.Tensors(i))
                    self.tensors.append(tensor_)
        if np is None:
            if not subGraph.InputsIsNone():
                self.inputs = []
                self.inputs.extend(subGraph.Inputs(i) for i in range(subGraph.InputsLength()))
        elif not subGraph.InputsIsNone():
            self.inputs = subGraph.InputsAsNumpy()
        if not subGraph.OutputsIsNone():
            if np is None:
                self.outputs = []
                self.outputs.extend(
                    subGraph.Outputs(i) for i in range(subGraph.OutputsLength())
                )
            else:
                self.outputs = subGraph.OutputsAsNumpy()
        if not subGraph.OperatorsIsNone():
            self.operators = []
            for i in range(subGraph.OperatorsLength()):
                if subGraph.Operators(i) is None:
                    self.operators.append(None)
                else:
                    operator_ = tflite.Operator.OperatorT.InitFromObj(subGraph.Operators(i))
                    self.operators.append(operator_)
        self.name = subGraph.Name()

    # SubGraphT
    def Pack(self, builder):
        if self.tensors is not None:
            tensorslist = [self.tensors[i].Pack(builder) for i in range(len(self.tensors))]
            SubGraphStartTensorsVector(builder, len(self.tensors))
            for i in reversed(range(len(self.tensors))):
                builder.PrependUOffsetTRelative(tensorslist[i])
            tensors = builder.EndVector(len(self.tensors))
        if self.inputs is not None:
            if np is not None and type(self.inputs) is np.ndarray:
                inputs = builder.CreateNumpyVector(self.inputs)
            else:
                SubGraphStartInputsVector(builder, len(self.inputs))
                for i in reversed(range(len(self.inputs))):
                    builder.PrependInt32(self.inputs[i])
                inputs = builder.EndVector(len(self.inputs))
        if self.outputs is not None:
            if np is not None and type(self.outputs) is np.ndarray:
                outputs = builder.CreateNumpyVector(self.outputs)
            else:
                SubGraphStartOutputsVector(builder, len(self.outputs))
                for i in reversed(range(len(self.outputs))):
                    builder.PrependInt32(self.outputs[i])
                outputs = builder.EndVector(len(self.outputs))
        if self.operators is not None:
            operatorslist = [
                self.operators[i].Pack(builder) for i in range(len(self.operators))
            ]
            SubGraphStartOperatorsVector(builder, len(self.operators))
            for i in reversed(range(len(self.operators))):
                builder.PrependUOffsetTRelative(operatorslist[i])
            operators = builder.EndVector(len(self.operators))
        if self.name is not None:
            name = builder.CreateString(self.name)
        SubGraphStart(builder)
        if self.tensors is not None:
            SubGraphAddTensors(builder, tensors)
        if self.inputs is not None:
            SubGraphAddInputs(builder, inputs)
        if self.outputs is not None:
            SubGraphAddOutputs(builder, outputs)
        if self.operators is not None:
            SubGraphAddOperators(builder, operators)
        if self.name is not None:
            SubGraphAddName(builder, name)
        return SubGraphEnd(builder)
