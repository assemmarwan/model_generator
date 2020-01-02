// Copyright (c) 2019, Assem Marwan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Model Generator', {
    refresh: frm => {
        frm.disable_save();
        frm.page.set_primary_action('Generate', () => {
            generate_doc(frm);
        });
    },
    onload: frm => {
        frm.set_query("reference_doctype", () => {
            return {
                "filters": {
                    "istable": 0
                }
            };
        });
    },
    reference_doctype: frm => {
        const doctype = frm.doc.reference_doctype;
        if (doctype)
            frappe.model.with_doctype(doctype, () => set_field_options(frm));
        else
            reset_filter_and_field(frm);

    }
});

const reset_filter_and_field = (frm) => {
    const parent_wrapper = frm.fields_dict.fields_multicheck.$wrapper;
    parent_wrapper.empty();
    frm.fields_multicheck = {};
};

const set_field_options = (frm) => {
    const parent_wrapper = frm.fields_dict.fields_multicheck.$wrapper;
    const doctype = frm.doc.reference_doctype;
    const related_doctypes = get_doctypes(doctype);

    parent_wrapper.empty();
    // Add 'Select All' and 'Unselect All' button
    make_multiselect_buttons(parent_wrapper);
    frm.fields_multicheck = {};
    related_doctypes.forEach(dt =>
        frm.fields_multicheck[dt.doctype] = add_doctype_field_multicheck_control(dt.doctype, parent_wrapper, dt.fieldname));

    frm.refresh();
};

const make_multiselect_buttons = parent_wrapper => {
    const button_container = $(parent_wrapper)
        .append('<div class="flex"></div>')
        .find('.flex');

    ["Select All", "Unselect All"].map(d => {
        frappe.ui.form.make_control({
            parent: $(button_container),
            df: {
                label: __(d),
                fieldname: frappe.scrub(d),
                fieldtype: "Button",
                click: () => {
                    checkbox_toggle(d !== 'Select All');
                }
            },
            render_input: true
        });
    });

    $(button_container).find('.frappe-control').map((index, button) => {
        $(button).css({"margin-right": "1em"});
    });

    function checkbox_toggle(checked) {
        $(parent_wrapper).find('[data-fieldtype="MultiCheck"]').map((index, element) => {
            $(element).find(`:checkbox`).prop("checked", checked).trigger('click');
        });
    }

};

const get_doctypes = parentdt => [{doctype: parentdt}].concat(
    frappe.meta.get_table_fields(parentdt).map((df) => {
        return {
            doctype: df.options, fieldname: df.fieldname
        };
    }));

const add_doctype_field_multicheck_control = (doctype, parent_wrapper, field = '') => {
    const fields = get_fields(doctype);

    console.log(fields);

    const options = fields
        .map(df => {
            return {
                label: `${df.label} (${df.fieldtype})`,
                value: `${df.fieldname}:${df.fieldtype}`,
                danger: df.reqd,
                checked: 1
            };
        });
    const multicheck_control = frappe.ui.form.make_control({
        parent: parent_wrapper,
        df: {
            "label": doctype,
            "fieldname": field,
            "fieldtype": "MultiCheck",
            "options": options,
            "columns": 3,
        },
        render_input: true
    });

    multicheck_control.refresh_input();
    return multicheck_control;
};

const generate_doc = frm => {
    let columns = {};
    Object.keys(frm.fields_multicheck).forEach(dt => {
        const options = frm.fields_multicheck[dt].get_checked_options();

        let key;
        if (frm.fields_multicheck[dt].df.fieldname === '')
            key = dt;
        else
            key = dt + ':' + frm.fields_multicheck[dt].df.fieldname;
        columns[key] = options;
    });
    console.log(columns);
    // TODO: Preprocess the result above and call the python function to generate the file.
};


const filter_fields = df => frappe.model.is_value_type(df) && !df.hidden;
const get_fields = dt => frappe.meta.get_docfields(dt).filter(filter_fields);