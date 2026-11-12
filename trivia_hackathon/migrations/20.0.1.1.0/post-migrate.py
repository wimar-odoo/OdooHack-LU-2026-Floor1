def migrate(cr, version):
    """ The PIN of the team is no longer stored in the database, only in the session of each user. """
    cr.execute("DELETE FROM ir_config_parameter WHERE key = 'trivia_hackathon.master_pin'")
