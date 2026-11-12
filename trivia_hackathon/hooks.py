from markupsafe import Markup


def post_init_hook(env):
    _install_french(env)
    _post_welcome_message(env)


def _install_french(env):
    """ The game is played in English or in French, depending on the language of the user. """
    if env["res.lang"]._activate_lang("fr_FR"):
        modules = env["ir.module.module"].search([("state", "in", ("installed", "to install", "to upgrade"))])
        modules._update_translations(["fr_FR"])


def _post_welcome_message(env):
    body = Markup(
        "<p>🧀 <b>Welcome to the Trivi'Hackathon! · Bienvenue au Trivi'Hackathon !</b></p>"
        "<p>🇬🇧 Six non-profit organisations need your help. Solve their challenges on the <i>Game Board</i> "
        "to collect the six wedges: every wedge you win will be announced here. "
        "The game is also available in French: change your language in your preferences.</p>"
        "<p>🇫🇷 Six ASBL ont besoin de votre aide. Résolvez leurs challenges sur le <i>Plateau de jeu</i> "
        "pour collectionner les six parts : chaque part gagnée sera annoncée ici. "
        "Le jeu est aussi disponible en anglais : changez de langue dans vos préférences.</p>"
    )
    env.ref("trivia_hackathon.channel_trivia").message_post(
        body=body,
        author_id=env.ref("base.partner_root").id,
        message_type="comment",
        subtype_xmlid="mail.mt_comment",
    )
