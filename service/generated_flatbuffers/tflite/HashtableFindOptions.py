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

class HashtableFindOptions(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsHashtableFindOptions(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = HashtableFindOptions()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def HashtableFindOptionsBufferHasIdentifier(cls, buf, offset, size_prefixed=False):
        return flatbuffers.util.BufferHasIdentifier(buf, offset, b"\x54\x46\x4C\x33", size_prefixed=size_prefixed)

    # HashtableFindOptions
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

def HashtableFindOptionsStart(builder): builder.StartObject(0)
def HashtableFindOptionsEnd(builder): return builder.EndObject()


class HashtableFindOptionsT(object):

    # HashtableFindOptionsT
    def __init__(self):
        pass

    @classmethod
    def InitFromBuf(cls, buf, pos):
        hashtableFindOptions = HashtableFindOptions()
        hashtableFindOptions.Init(buf, pos)
        return cls.InitFromObj(hashtableFindOptions)

    @classmethod
    def InitFromObj(cls, hashtableFindOptions):
        x = HashtableFindOptionsT()
        x._UnPack(hashtableFindOptions)
        return x

    # HashtableFindOptionsT
    def _UnPack(self, hashtableFindOptions):
        if hashtableFindOptions is None:
            return

    # HashtableFindOptionsT
    def Pack(self, builder):
        HashtableFindOptionsStart(builder)
        return HashtableFindOptionsEnd(builder)
