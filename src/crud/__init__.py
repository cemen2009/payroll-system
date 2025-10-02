from crud.department import (
    fetch_department_by_id,
    fetch_departments,
    create_department_entity,
    update_department_entity,
)
from crud.position import (
    fetch_position_by_id,
    fetch_positions,
    create_position_entity,
    update_position_entity
)
from crud.employee import (
    fetch_employee_by_id,
    fetch_employees,
    create_employee_entity,
    update_employee_entity,
)
from crud.vacation import (
    fetch_vacation_by_id,
    fetch_vacations,
    create_vacation_entity,
    update_vacation_entity
)
from crud.work_report import (
    fetch_work_report,
    fetch_work_reports,
    create_work_report_entity,
    update_work_report_entity,
)
from crud.common import count_entities, delete_entity