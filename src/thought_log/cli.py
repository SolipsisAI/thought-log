import click


@click.group()
def cli():
    pass


@cli.command()
@click.argument("text")
def add(text):
    from thought_log.utils import DATA_DIR, ROOT_DIR

    print(f"Input: {text}|{ROOT_DIR} {DATA_DIR}")


@cli.command()
@click.option("--model_name", "-m")
@click.option("--tokenizer_name", "-t")
@click.option("--config_name", "-c")
@click.option("--classifier_name", "-cf")
@click.option("--pipeline/--no-pipeline", "-p")
@click.option("--max_length", default=1000)
def interact(
    model_name, tokenizer_name, config_name, classifier_name, pipeline, max_length
):
    from thought_log.interact import interact

    interact(
        model_name, tokenizer_name, config_name, classifier_name, pipeline, max_length
    )
