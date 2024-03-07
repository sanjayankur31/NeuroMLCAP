# CaDynamics.mod  Ca_LVA.mod  Gfluct.mod  Im.mod   K_T.mod    Nap.mod   NMDA.mod          ProbUDFsyn.mod  tonic.mod
# Ca_HVA.mod      epsp.mod    Ih.mod      K_P.mod  Kv3_1.mod  NaTg.mod  ProbAMPANMDA.mod  SK.mod
#
echo "Compiling mod files"
nrnivmodl .

parallel_run() {
    parallel -j $1 --\
        "pynml-channelanalysis SK.channel.nml -stepTargetVoltage 5 -temperature 6.3 -v"\
        "pynml-channelanalysis Kv3_1.channel.nml -stepTargetVoltage 5 -temperature 6.3"\
        "pynml-channelanalysis NaTg.channel.nml -stepTargetVoltage 5 -temperature 6.3"\
        "pynml-channelanalysis Nap.channel.nml -stepTargetVoltage 5 -temperature 6.3 -duration 20000"\
        "pynml-channelanalysis K_P.channel.nml -stepTargetVoltage 5 -temperature 6.3"\
        "pynml-channelanalysis K_T.channel.nml -stepTargetVoltage 5 -temperature 6.3"\
        "pynml-channelanalysis Ca_HVA.channel.nml -stepTargetVoltage 5 -temperature 6.3"\
        "pynml-channelanalysis Ca_LVA.channel.nml -stepTargetVoltage 5 -temperature 6.3"\
        "pynml-channelanalysis Ih.channel.nml -stepTargetVoltage 5 -temperature 6.3"\
        "pynml-channelanalysis Im.channel.nml -stepTargetVoltage 5 -temperature 6.3"

}

serial_run () {
    pynml-channelanalysis SK.channel.nml -stepTargetVoltage 5 -temperature 6.3 -v
    pynml-channelanalysis Kv3_1.channel.nml -stepTargetVoltage 5 -temperature 6.3
    pynml-channelanalysis NaTg.channel.nml -stepTargetVoltage 5 -temperature 6.3
    pynml-channelanalysis Nap.channel.nml -stepTargetVoltage 5 -temperature 6.3 -duration 20000
    pynml-channelanalysis K_P.channel.nml -stepTargetVoltage 5 -temperature 6.3
    pynml-channelanalysis K_T.channel.nml -stepTargetVoltage 5 -temperature 6.3
    pynml-channelanalysis Ca_HVA.channel.nml -stepTargetVoltage 5 -temperature 6.3
    pynml-channelanalysis Ca_LVA.channel.nml -stepTargetVoltage 5 -temperature 6.3
    pynml-channelanalysis Ih.channel.nml -stepTargetVoltage 5 -temperature 6.3
    pynml-channelanalysis Im.channel.nml -stepTargetVoltage 5 -temperature 6.3
}

echo "Analysing mod files"

#serial_run

    #pynml-channelanalysis Ca_HVA.channel.nml -stepTargetVoltage 5 -temperature 6.3
    pynml-channelanalysis Kv3_1.channel.nml -stepTargetVoltage 5 -temperature 6.3
## if gnu parallel is available, use the parallel run, argument is number of parallel jobs:
# parallel_run 6
