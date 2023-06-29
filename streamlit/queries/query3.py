def query_3():
    # Pipeline stages
    first_stage = {
        "$project": {
            "_id": 0,
            "visits": 1
        }
    }
    unwind_visits_stage = {"$unwind": "$visits"}
    
    filter_exams = {
        '$match': {
            'visits.exams': {'$exists': True},
            'visits.name': {'$nin': ['EMERGENZA', 'DAY_HOSPITAL', 'ANAMNESI']}
         }
    }
    unwind_exams_stage = {"$unwind": "$visits.exams"}
    group_stage = {
        "$group": {
            "_id": "$visits.exams.name",
            "count": {"$sum": 1}
        }
    }
    project_stage = {
        "$project": {
            "exam_name": "$_id",
            "count": 1,
            "_id": 0
        }
    }
    
    order_stage = {
        "$sort": {"count": -1, "exam_name": 1}
    }

    # Aggregation pipeline
    pipeline = [
        first_stage,
        unwind_visits_stage,
        filter_exams,
        unwind_exams_stage,
        group_stage,
        project_stage,
        # order_stage
    ]

    return pipeline