parallel_processes = 8


rule create_analysis:
    input:
        expand("analysis.{cellname}.toml", cellname=config['cellname'])
    output:
        "simulation.txt",
    shell:
        "python3 neuroml-cap.py --analyse {input}"

rule run_analysis:
    input:
        rules.create_analysis.output
    output:
        touch("run_analysis.done")
    shell:
        "pushd $(cat {input}) && ../run_parallel.sh {parallel_processes} && popd ; rm simulation.txt"

rule run_sim_analysis_and_plot:
    input:
        rules.create_analysis.output
        rules.run_analysis.output
    output:
        touch("plotting.done")
    shell:
        "python3 neuroml-cap.py --plot $(cat {input})"

# has to be at bottom because run_analysis needs to be defined
rule all:
    input: rules.run_analysis.output
    default_target:True
