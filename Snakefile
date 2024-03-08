parallel_processes = 8


rule create_analysis:
    input:
        expand("analysis.{filename}.toml", filename=config['cellname'])
    output:
        "simulation.txt"
    shell:
        "python3 analysis.py {input}"

rule run_analysis:
    input:
        rules.create_analysis.output
    output:
        touch("done.done")
    shell:
        "pushd $(cat {input}) && ../run_parallel.sh {parallel_processes} && popd"

rule all:
    input: rules.run_analysis.output
    default_target:True
