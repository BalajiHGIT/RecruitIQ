
def calculate_match_score(candidate_skills, required_skills):
    if not required_skills:
        return 0

    candidate_set = {
        skill.strip().lower()
        for skill in candidate_skills
    }

    required_set = {
        skill.strip().lower()
        for skill in required_skills
    }

    matched_skills = candidate_set.intersection(required_set)

    score = (len(matched_skills) / len(required_set)) * 100

    return round(score, 2)


def get_matching_skills(candidate_skills, required_skills):
    candidate_set = {
        skill.strip().lower()
        for skill in candidate_skills
    }

    return [
        skill for skill in required_skills
        if skill.strip().lower() in candidate_set
    ]
