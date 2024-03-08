parallel_processes = 8


rule create_analysis:
    input:
        expand("analysis.{filename}.toml", filename=config['cellname'])
    output:
        "simulation.txt",
    shell:
        "python3 analysis.py {input}"

rule run_analysis:
    input:
        rules.create_analysis.output
    output:
        touch("run_analysis.done")
    shell:
        "pushd $(cat {input}) && ../run_parallel.sh {parallel_processes} && popd ; rm simulation.txt"

# has to be at bottom because run_analysis needs to be defined
rule all:
    input: rules.run_analysis.output
    default_target:True
