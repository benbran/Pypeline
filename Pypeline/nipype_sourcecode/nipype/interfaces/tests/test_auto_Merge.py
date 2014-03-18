# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from nipype.testing import assert_equal
from nipype.interfaces.utility import Merge

def test_Merge_inputs():
    input_map = dict(axis=dict(usedefault=True,
    ),
    ignore_exception=dict(nohash=True,
    usedefault=True,
    ),
    no_flatten=dict(usedefault=True,
    ),
    )
    inputs = Merge.input_spec()

    for key, metadata in input_map.items():
        for metakey, value in metadata.items():
            yield assert_equal, getattr(inputs.traits()[key], metakey), value

def test_Merge_outputs():
    output_map = dict(out=dict(),
    )
    outputs = Merge.output_spec()

    for key, metadata in output_map.items():
        for metakey, value in metadata.items():
            yield assert_equal, getattr(outputs.traits()[key], metakey), value

