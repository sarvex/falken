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

class SignatureDef(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsSignatureDef(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = SignatureDef()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def SignatureDefBufferHasIdentifier(cls, buf, offset, size_prefixed=False):
        return flatbuffers.util.BufferHasIdentifier(buf, offset, b"\x54\x46\x4C\x33", size_prefixed=size_prefixed)

    # SignatureDef
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # SignatureDef
    def Inputs(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            x = self._tab.Vector(o)
            x += flatbuffers.number_types.UOffsetTFlags.py_type(j) * 4
            x = self._tab.Indirect(x)
            from tflite.TensorMap import TensorMap
            obj = TensorMap()
            obj.Init(self._tab.Bytes, x)
            return obj
        return None

    # SignatureDef
    def InputsLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        return self._tab.VectorLen(o) if o != 0 else 0

    # SignatureDef
    def InputsIsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        return o == 0

    # SignatureDef
    def Outputs(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            x = self._tab.Vector(o)
            x += flatbuffers.number_types.UOffsetTFlags.py_type(j) * 4
            x = self._tab.Indirect(x)
            from tflite.TensorMap import TensorMap
            obj = TensorMap()
            obj.Init(self._tab.Bytes, x)
            return obj
        return None

    # SignatureDef
    def OutputsLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        return self._tab.VectorLen(o) if o != 0 else 0

    # SignatureDef
    def OutputsIsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        return o == 0

    # SignatureDef
    def MethodName(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        return self._tab.String(o + self._tab.Pos) if o != 0 else None

    # SignatureDef
    def Key(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        return self._tab.String(o + self._tab.Pos) if o != 0 else None

def SignatureDefStart(builder): builder.StartObject(4)
def SignatureDefAddInputs(builder, inputs): builder.PrependUOffsetTRelativeSlot(0, flatbuffers.number_types.UOffsetTFlags.py_type(inputs), 0)
def SignatureDefStartInputsVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def SignatureDefAddOutputs(builder, outputs): builder.PrependUOffsetTRelativeSlot(1, flatbuffers.number_types.UOffsetTFlags.py_type(outputs), 0)
def SignatureDefStartOutputsVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def SignatureDefAddMethodName(builder, methodName): builder.PrependUOffsetTRelativeSlot(2, flatbuffers.number_types.UOffsetTFlags.py_type(methodName), 0)
def SignatureDefAddKey(builder, key): builder.PrependUOffsetTRelativeSlot(3, flatbuffers.number_types.UOffsetTFlags.py_type(key), 0)
def SignatureDefEnd(builder): return builder.EndObject()

import tflite.TensorMap
try:
    from typing import List
except:
    pass

class SignatureDefT(object):

    # SignatureDefT
    def __init__(self):
        self.inputs = None  # type: List[tflite.TensorMap.TensorMapT]
        self.outputs = None  # type: List[tflite.TensorMap.TensorMapT]
        self.methodName = None  # type: str
        self.key = None  # type: str

    @classmethod
    def InitFromBuf(cls, buf, pos):
        signatureDef = SignatureDef()
        signatureDef.Init(buf, pos)
        return cls.InitFromObj(signatureDef)

    @classmethod
    def InitFromObj(cls, signatureDef):
        x = SignatureDefT()
        x._UnPack(signatureDef)
        return x

    # SignatureDefT
    def _UnPack(self, signatureDef):
        if signatureDef is None:
            return
        if not signatureDef.InputsIsNone():
            self.inputs = []
            for i in range(signatureDef.InputsLength()):
                if signatureDef.Inputs(i) is None:
                    self.inputs.append(None)
                else:
                    tensorMap_ = tflite.TensorMap.TensorMapT.InitFromObj(signatureDef.Inputs(i))
                    self.inputs.append(tensorMap_)
        if not signatureDef.OutputsIsNone():
            self.outputs = []
            for i in range(signatureDef.OutputsLength()):
                if signatureDef.Outputs(i) is None:
                    self.outputs.append(None)
                else:
                    tensorMap_ = tflite.TensorMap.TensorMapT.InitFromObj(signatureDef.Outputs(i))
                    self.outputs.append(tensorMap_)
        self.methodName = signatureDef.MethodName()
        self.key = signatureDef.Key()

    # SignatureDefT
    def Pack(self, builder):
        if self.inputs is not None:
            inputslist = [self.inputs[i].Pack(builder) for i in range(len(self.inputs))]
            SignatureDefStartInputsVector(builder, len(self.inputs))
            for i in reversed(range(len(self.inputs))):
                builder.PrependUOffsetTRelative(inputslist[i])
            inputs = builder.EndVector(len(self.inputs))
        if self.outputs is not None:
            outputslist = [self.outputs[i].Pack(builder) for i in range(len(self.outputs))]
            SignatureDefStartOutputsVector(builder, len(self.outputs))
            for i in reversed(range(len(self.outputs))):
                builder.PrependUOffsetTRelative(outputslist[i])
            outputs = builder.EndVector(len(self.outputs))
        if self.methodName is not None:
            methodName = builder.CreateString(self.methodName)
        if self.key is not None:
            key = builder.CreateString(self.key)
        SignatureDefStart(builder)
        if self.inputs is not None:
            SignatureDefAddInputs(builder, inputs)
        if self.outputs is not None:
            SignatureDefAddOutputs(builder, outputs)
        if self.methodName is not None:
            SignatureDefAddMethodName(builder, methodName)
        if self.key is not None:
            SignatureDefAddKey(builder, key)
        return SignatureDefEnd(builder)
